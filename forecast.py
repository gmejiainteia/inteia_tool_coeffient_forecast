import pandas as pd
import numpy as np

import os
import datetime
import dateutil

from autots import AutoTS

import plotly.express as px

def calculate_template(*args,**kwargs):
    file_path=os.path.join('data','template_forecast.xlsx')
    with open(file_path, "rb") as template_file:
        template = template_file.read()
    return template

class Deflect:
    def __init__(self, *args,**kwargs):
        self.run()
    
    def run(self,*args,**kwargs):
        date=datetime.datetime.today()
        date=date.date()
        date=date + dateutil.relativedelta.relativedelta(day=31)

        file_path=os.path.join("data","ipc.xlsx")
        df=pd.read_excel(file_path)

        df_tmp=pd.DataFrame(pd.date_range(start=datetime.datetime(df["year"].min(),1,1),end=datetime.datetime(df["year"].max(),12,31),freq='M'),columns=["date"])
        df_tmp["date"]=pd.to_datetime(df_tmp["date"])
        df_tmp["year"]=df_tmp["date"].dt.year
        df_tmp["value"]=1.0

        df_base=pd.merge(df_tmp,df)
        df_base["ipcm"]=(1+df_base["ipc"])**(1/12)-1
        df_base["constant"]=np.nan
        df_base["factor"]=np.nan

        date_horizon=date.strftime(format=r"%Y-%m-%d")

        df=df_base.query( f"date<='{date_horizon}'", engine='python')

        df.sort_values(by=["date"],ascending=False,inplace=True)
        df.reset_index(drop=True, inplace=True)

        for i in range(df.shape[0]):
            if i==0:
                df.loc[i, 'factor']=1
                df.loc[i, 'constant']=df.loc[i, 'value']
            else:
                df.loc[i, 'factor']=df.loc[i-1, 'factor']/(1+df.loc[i-1, 'ipcm'])
                df.loc[i, 'constant']=df.loc[i, 'value']/(1+df.loc[i, 'ipcm'])

        df["x"]=df["constant"]/df["factor"]

        df.sort_values(by=["date"],ascending=True,inplace=True)
        df.reset_index(drop=True, inplace=True)

        df_tmp=df_base.query( f"date>'{date_horizon}'", engine='python')

        df_tmp.sort_values(by=["date"],ascending=True,inplace=True)
        df_tmp.reset_index(drop=True, inplace=True)

        for i in range(df_tmp.shape[0]):
            if i==0:
                df_tmp.loc[i, 'factor']=df.loc[df.shape[0]-1, 'factor']/(1-df.loc[df.shape[0]-1, 'ipcm'])
                df_tmp.loc[i, 'constant']=df_tmp.loc[i, 'value']/(1-df_tmp.loc[i, 'ipcm'])
            else:
                df_tmp.loc[i, 'factor']=df_tmp.loc[i-1, 'factor']/(1-df_tmp.loc[i-1, 'ipcm'])
                df_tmp.loc[i, 'constant']=df_tmp.loc[i, 'value']/(1-df_tmp.loc[i, 'ipcm'])

        df_tmp["x"]=df_tmp["constant"]/df_tmp["factor"]

        df_tmp.sort_values(by=["date"],ascending=True,inplace=True)
        df_tmp.reset_index(drop=True, inplace=True)

        df=pd.concat([df,df_tmp])
        
        df.set_index(keys=['date'],inplace=True)

        deflect=df['x'].to_dict()

        self.deflect=deflect

class ForecastCCT:
    def __init__(self, *args,**kwargs):
        self.df = kwargs.get('df')

        self.calculate_data()
        self.calculate_model()
        self.calculate_prediction()
        
    def calculate_data(self,*args,**kwargs):
        df=self.df.copy()

        groups = [
            pd.Grouper(key="date_hour", freq="M")
        ]

        aggs = {
            'value':  ['sum']
        }

        df = df.groupby(groups).agg(aggs).reset_index()
        df.columns = df.columns.map("_".join).str.strip("_")
        df.rename(columns=dict(value_sum='value'), inplace=True)

        df_tmp=df.copy()

        df_tmp['date_hour_min'] = df_tmp['date_hour'].apply(lambda x: pd.Timestamp(x.year, 1, 31))
        df_tmp['date_hour_max'] = df_tmp['date_hour'].apply(lambda x: pd.Timestamp(x.year, 12, 31))

        date_hour_horizon=df_tmp['date_hour'].max()
        df_tmp.query('date_hour==@date_hour_horizon', inplace=True)

        date_hour_min=df_tmp['date_hour_min'].min()
        date_hour_max=df_tmp['date_hour_max'].max()

        forecast_length=dateutil.relativedelta.relativedelta(date_hour_max, date_hour_horizon).months

        if forecast_length==0:
            date_hour_min=pd.Timestamp(date_hour_min.year+1, 1, 31)
            date_hour_max=pd.Timestamp(date_hour_max.year+1, 12, 31)
            date_hour_horizon=date_hour_min
            forecast_length=12

        self.df=df
        self.date_hour_horizon=date_hour_horizon
        self.date_hour_min=date_hour_min
        self.date_hour_max=date_hour_max
        self.forecast_length=forecast_length

    def calculate_model(self,*args,**kwargs):

        model = AutoTS(
            forecast_length=self.forecast_length,
            frequency='infer',
            prediction_interval=0.95,
            ensemble='fast',
            model_list="superfast",
            transformer_list="auto",
            drop_most_recent=0,
            max_generations=3,
            num_validations=2,
            validation_method="backwards",
            no_negatives=True,
        )

        model = model.fit(self.df, date_col='date_hour', value_col='value')
        
        self.model = model
    
    def calculate_prediction(self,*args,**kwargs):
        prediction=self.model.predict()
        
        data=[]

        df_tmp=self.df
        df_tmp['state']='real'
        data.append(df_tmp)
        print(df_tmp)

        df_tmp=prediction.forecast
        df_tmp["date_hour"]=df_tmp.index
        df_tmp['state']='mean'
        df_tmp.reset_index(drop=True,inplace=True)
        df_tmp.rename(columns={0:'value'}, inplace=True)
        data.append(df_tmp)

        df_tmp=prediction.upper_forecast
        df_tmp["date_hour"]=df_tmp.index
        df_tmp['state']='upper'
        df_tmp.reset_index(drop=True,inplace=True)
        df_tmp.rename(columns={0:'value'}, inplace=True)
        data.append(df_tmp)

        df_tmp=prediction.lower_forecast
        df_tmp["date_hour"]=df_tmp.index
        df_tmp['state']='lower'
        df_tmp.reset_index(drop=True,inplace=True)
        df_tmp.rename(columns={0:'value'}, inplace=True)
        data.append(df_tmp)

        #calcular metodo total
        df=pd.concat(data, ignore_index=True)
        df_tmp=df.copy()

        tmp=Deflect()
        df_tmp['value']=df_tmp['date_hour'].map(tmp.deflect)*df['value']

        df['deflect']=False
        df_tmp['deflect']=True

        date_hour_min=self.date_hour_min
        date_hour_max=self.date_hour_max
        df=pd.concat(data,ignore_index=True)
        df.query('date_hour>=@date_hour_min & date_hour<=@date_hour_max', inplace=True)

        df=pd.pivot_table(df, index='date_hour', columns='state', values='value').reset_index()
        df.sort_values(by='date_hour', inplace=True)

        reference_column='real'

        if reference_column not in df.columns.tolist():
            df[reference_column]=np.nan

        columns=['real', 'lower', 'mean', 'upper']


        for column in columns:
            df[column]=df[column].fillna(df[reference_column])

        df_tmp=df.copy()

        for column in columns:
            df_tmp[column] = df_tmp[column].cumsum()

        df['cumsum']=False
        df_tmp['cumsum']=True

        df=pd.concat([df, df_tmp], ignore_index=True)

        df=pd.melt(df, id_vars=['date_hour', 'cumsum'])

        df_tmp=df.copy()

        tmp=Deflect()
        df_tmp['value']=df_tmp['date_hour'].map(tmp.deflect)*df['value']

        df['deflect']=False
        df_tmp['deflect']=True

        df=pd.concat([df, df_tmp], ignore_index=True)
        df.dropna(inplace=True)
        
        columns=['date_hour', 'cumsum', 'deflect', 'state', 'value']
        df=df[columns]

        self.df_prediction=df

def calculate_terms(*args,**kwargs):
    terms={
        'date_hour': 'FECHA', 
        'cumsum':'ACUMULADO', 
        'deflect':'DEFLECTADO', 
        'state':'ESCENARIO', 
        'value': 'VALOR',
        'real':'REAL',
        'lower':'INFERIOR',
        'mean':'MEDIO',
        'upper':'ALTO',
    }
    return terms

def calculate_df_forecast(*args,**kwargs):
    df=kwargs.get('df').copy()
    
    terms=calculate_terms()

    df['cumsum']=df['cumsum'].map({False:'NO ACUMULADO', True: 'ACUMULADO'})
    df['deflect']=df['deflect'].map({False:'NO DEFLECTADO', True: 'DEFLECTADO'})
    df['state']=df['state'].map(terms)
    df.rename(columns=terms, inplace=True)

    return df

def calculate_figure_forecast(*args,**kwargs):
    df=kwargs.get('df').copy()

    cumsum=kwargs.get('cumsum')
    deflect=kwargs.get('deflect')

    date_hour_horizon=kwargs.get('date_hour_horizon')

    date_hour_min=kwargs.get('date_hour_min')
    date_hour_max=kwargs.get('date_hour_max')

    terms=calculate_terms()

    cumsum_text={False:'', True: 'ACUMULADO'}.get(cumsum)
    deflect_text={False:'', True: 'DEFLECTADO'}.get(deflect)

    title=f'ING CCT {cumsum_text} {deflect_text} - FECHA HORIZONTE: {date_hour_horizon.strftime("%Y-%m-%d")} - FECHA MIN: {date_hour_min.strftime("%Y-%m-%d")} - FECHA MAX: {date_hour_max.strftime("%Y-%m-%d")}'

    df_tmp=df.query('cumsum==@cumsum & deflect==@deflect', inplace=False).reset_index(drop=True)

    df_tmp['state']=df_tmp['state'].map(terms)

    df_tmp.rename(columns=terms, inplace=True)

    if 'real' in df_tmp.columns.tolist():
        order=['real', 'lower', 'mean', 'upper']
        color=[px.colors.sequential.Turbo[5], px.colors.sequential.Turbo[1], px.colors.sequential.Turbo[2], px.colors.sequential.Turbo[3]]
    else:
        order=['upper', 'lower', 'mean']
        color=[px.colors.sequential.Turbo[2], px.colors.sequential.Turbo[3], px.colors.sequential.Turbo[1]]

    order=[terms.get(i) for i in order]

    fig=px.bar(
        df_tmp, 
        x=terms.get('date_hour'), 
        y=terms.get('value'),  
        color=terms.get('state'), 
        color_discrete_map=dict(zip(order, color)), 
        category_orders={terms.get('state'): order}, 
        barmode='group', 
        
        text_auto=True,
    )

    fig.update_layout(title=dict(text=title))

    fig.update_xaxes(title_text='FECHA', tickformat = "%b-%Y",dtick="M1")
    fig.update_yaxes(title_text='ING CCT', tickformat = "$.4s")

    fig.add_vline(x=date_hour_horizon, line_dash='solid')
    fig.add_vline(x=date_hour_max, line_dash='solid')

    fig.add_vrect(x0=date_hour_horizon, x1=date_hour_max, annotation_text='FORECAST', annotation_position="top left", fillcolor="yellow", opacity=0.10, line_width=0)

    fig.for_each_annotation(lambda title: title.update(font=dict(size=15)))

    fig.for_each_xaxis(lambda axis: axis.title.update(font=dict(size=15)))
    fig.for_each_yaxis(lambda axis: axis.title.update(font=dict(size=15)))    

    fig.update_traces(textfont=dict(size=25))

    fig.for_each_trace(lambda trace: trace.update(xperiod="M1", xperiodalignment="start"))

    return fig


def calculate_results(*args,**kwargs):
    df=kwargs.get('df').copy()

    forecast=ForecastCCT(**dict(df=df))
    df_prediction=forecast.df_prediction

    date_hour_horizon=forecast.date_hour_horizon
    date_hour_min=forecast.date_hour_min
    date_hour_max=forecast.date_hour_max

    df_elements=[]

    df_tmp=calculate_df_forecast(**dict(df=df_prediction))
    df_elements.append(dict(name='FORECAST', df=df_tmp))

    fig_elements=[]

    fig=calculate_figure_forecast(**dict(df=df_prediction, date_hour_horizon=date_hour_horizon, date_hour_min=date_hour_min, date_hour_max=date_hour_max, deflect=False, cumsum=False))
    fig_elements.append(dict(name='ING CCT', fig=fig))


    fig=calculate_figure_forecast(**dict(df=df_prediction, date_hour_horizon=date_hour_horizon, date_hour_min=date_hour_min, date_hour_max=date_hour_max, deflect=False, cumsum=True))
    fig_elements.append(dict(name='ING CCT ACUM', fig=fig))

    fig=calculate_figure_forecast(**dict(df=df_prediction, date_hour_horizon=date_hour_horizon, date_hour_min=date_hour_min, date_hour_max=date_hour_max, deflect=True, cumsum=False))
    fig_elements.append(dict(name='ING CCT DEFLECT', fig=fig))

    fig=calculate_figure_forecast(**dict(df=df_prediction, date_hour_horizon=date_hour_horizon, date_hour_min=date_hour_min, date_hour_max=date_hour_max, deflect=False, cumsum=False))
    fig_elements.append(dict(name='ING CCT ACUM DEFLECT', fig=fig))

    rst=dict(df_elements=df_elements, fig_elements=fig_elements)

    return rst

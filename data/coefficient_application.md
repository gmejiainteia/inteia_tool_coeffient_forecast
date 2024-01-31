# Documentación de la Aplicación de Cálculo de Coeficientes Salariales

## Introducción
Esta aplicación utiliza un modelo de LightGBM para predecir los salarios de los empleados basándose en características específicas. Calcula los coeficientes salariales al comparar los salarios reales con los salarios predichos por el modelo. La aplicación está implementada en Streamlit.

## Funcionamiento
La aplicación recopila datos de características de los empleados, utiliza un modelo de LightGBM para predecir los salarios, y luego calcula los coeficientes salariales. Proporciona visualizaciones interactivas de los datos y resultados.

## Modelos de Predicción
Se utiliza un modelo de LightGBM para predecir los salarios de los empleados. Este modelo se entrena utilizando GridSearchCV para encontrar los mejores parámetros.

## Ventajas de la Automatización del Proceso de Predicción Salarial
- Eficiencia: La automatización ahorra tiempo y recursos humanos al calcular los salarios.
- Precisión: Los modelos de Machine Learning pueden capturar patrones complejos para realizar predicciones más precisas.
- Escalabilidad: La automatización permite manejar grandes volúmenes de datos de manera eficiente.

## Potencial de la Herramienta
La herramienta tiene un gran potencial en la gestión de recursos humanos y la toma de decisiones basadas en datos. Facilita la optimización de los salarios y ayuda a identificar discrepancias entre los salarios reales y los estimados.

## Definiciones
- **Salario Real:** El salario actual percibido por el empleado.
- **Salario Predicho:** El salario estimado por el modelo de Machine Learning basado en características específicas del empleado.
- **Coeficiente Salarial:** La relación entre el salario real y el salario predicho.
- **Datos Categóricos:** Incluyen información como género, cargo y departamento.
- **Datos Numéricos:** Incluyen características como años de experiencia.
- **Datos de Fecha:** Pueden incluir fechas relevantes, como la fecha de contratación.

## Metodología de Cálculo
1. Se recopilan características de los empleados, incluyendo datos categóricos, numéricos y de fecha.
2. Estas características se utilizan como entrada para el modelo de LightGBM, que predice los salarios de los empleados.
3. Se calculan los coeficientes salariales comparando los salarios reales con los predichos.

# Documentación Técnica: Modelo de Predicción LightGBM

## Introducción
En esta documentación técnica, se detalla el funcionamiento y la implementación del modelo de predicción LightGBM utilizado en la aplicación de cálculo de coeficientes salariales.

## Modelo de Predicción LightGBM
LightGBM es una implementación de Gradient Boosting Framework desarrollada por Microsoft. Se caracteriza por su velocidad y eficiencia, especialmente en conjuntos de datos grandes. A continuación, se explican los aspectos clave de la implementación de LightGBM en la aplicación:

- **Entrenamiento del Modelo:** El modelo LightGBM se entrena utilizando la biblioteca scikit-learn. Se emplea una técnica de búsqueda de hiperparámetros GridSearchCV para encontrar la combinación óptima de parámetros, como la profundidad máxima del árbol, la tasa de aprendizaje, el número de estimadores y la proporción de columnas de árbol seleccionadas.
  
- **Características Utilizadas:** El modelo utiliza características específicas de los empleados, como datos categóricos (género, cargo, departamento), datos numéricos (años de experiencia, nivel educativo) y datos de fecha (fecha de contratación, fecha de nacimiento).

- **Predicción de Salarios:** Una vez entrenado el modelo, se utiliza para predecir los salarios estimados de los empleados en función de sus características. Estas predicciones se comparan con los salarios reales para calcular los coeficientes salariales.

## Ventajas del Modelo LightGBM
El uso del modelo LightGBM presenta varias ventajas en el contexto de la aplicación de cálculo de coeficientes salariales:

- **Eficiencia:** LightGBM es conocido por su eficiencia en el manejo de grandes conjuntos de datos, lo que permite un tiempo de entrenamiento rápido y predicciones ágiles.
  
- **Precisión:** La capacidad de LightGBM para capturar patrones complejos en los datos conduce a predicciones más precisas de los salarios de los empleados.
  
- **Flexibilidad:** LightGBM ofrece una amplia gama de hiperparámetros que se pueden ajustar para optimizar el rendimiento del modelo, lo que lo hace adaptable a diferentes conjuntos de datos y requisitos específicos de la aplicación.

## Conclusión
El modelo LightGBM desempeña un papel crucial en la aplicación de cálculo de coeficientes salariales, proporcionando predicciones precisas y eficientes basadas en las características de los empleados. Su implementación adecuada contribuye significativamente a la eficacia y la exactitud del proceso de estimación salarial.


## Contacto
Para más información, contáctenos en [cienciadatos@inteia.com.co](mailto:cienciadatos@inteia.com.co).

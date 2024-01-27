# HPC168 Data Receiver

Este es un programa en Python diseñado para recibir y procesar datos del contador de personas HPC168 a través de una conexión serial. El programa verifica la integridad de los datos recibidos y extrae información relevante, como el ID, el comando, la longitud y los datos de subida y bajada de pasajeros.

## Requisitos

- Python 3
- Biblioteca serial (`pyserial`)

## Instalación

1. Clona este repositorio en tu máquina local:

   ```bash
    git clone https://github.com/ErnestoLomar/HPC168.git

2. Instala las dependencias:

    ```bash
    pip install pyserial

## Uso

1. Conecta el contador de personas HPC168 a tu computadora a través del puerto serial (por ejemplo, /dev/ttyUSB0).

2. Ejecuta el programa:
   
   ```bash
   python hpc168_data_receiver.py

3. Observa la salida en la consola y el archivo de registro (log_mes_anio.txt).

## Configuración

1. Asegúrate de que el programa esté configurado con el puerto serial correcto y la velocidad de baudios.
   
   ```bash
   ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

## Contribuciones

¡Contribuciones son bienvenidas! Si encuentras un problema o tienes una mejora, por favor, abre un problema o envía una solicitud de extracción.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo LICENSE para obtener más detalles.


Este README proporciona información básica sobre cómo instalar y usar tu programa, así como detalles sobre configuración y contribuciones. Asegúrate de personalizarlo según las necesidades específicas de tu proyecto.

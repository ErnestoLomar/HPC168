import serial
import time
import logging
import datetime

# Obtener el nombre del mes y año actual
nombre_mes = datetime.datetime.now().strftime("%B")  # Obtiene el nombre del mes
nombre_anio = datetime.datetime.now().strftime("%Y")  # Obtiene el año en formato de 4 dígitos

# Construir el nombre del archivo de registro
nombre_archivo_log = f"log_{nombre_mes}_{nombre_anio}.txt"

# Configurar el módulo logging
logging.basicConfig(filename=nombre_archivo_log, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

if (ser.is_open):
    print("Conexion establecida")
    logging.info("Conexion establecida")
    
else:
    print("Conexion fallida")
    logging.error("Conexion fallida")

while True:
    
    try:
        
        data = bytearray(45)
        k, ID_H, ID_D, CM_H, CM_D, LEN_H, LEN_D, DATA1UP_D, DATA1DW_D, CHK_ARD_D = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        correct_set = False
        CHK_ARD_H_LSB = bytearray(2)
        CHK_HPC_H_LSB = bytearray(2)

        # Se prepara el espacio para los 45 datos que abarca la trama; se configuran a un valor inicial de 0x77.
        data = [0x77] * 45
        
        # Despliega aviso hacia el cuenta personas para preguntar sobre los datos hasta el momento de las subidas y bajadas de pasajeros.
        for byte in [0x02, 0x30, 0x30, 0x30, 0x31, 0x31, 0x33, 0x30, 0x30, 0x31, 0x34, 0x03]:
            ser.write([byte])
        
        # Limpiamos el buffer del serial por si hay algun dato basura.
        ser.flush()

        # Llena los datos en el arreglo con lo recibido por serial del cuenta personas.
        for k in range(1, 45):
            dato_serial = ser.read()
            data[k] = format(int.from_bytes(dato_serial, byteorder='big'), 'X')

        # Elimina el primer dato del array ya que no es necesario
        data.pop(0)
        
        print("Arreglo completo de datos recibidos: ", data)
        logging.info("Arreglo completo de datos recibidos: %s", data)

        # Se lee el primer byte del arreglo recibido por el CP para verificar si es STX (0x02)
        if data[0] != '2':
            print("El comienzo de la trama de datos STX es diferente al esperado. Se procede a esperar el siguiente dato.")
            logging.info("El comienzo de la trama de datos STX es diferente al esperado. Se procede a esperar el siguiente dato.")
            time.sleep(1)

        correct_set = True
        
        # Verificamos que todos los datos sean diferentes a 0xFF o 0x77 para asegurar que lo recibido por el CP son verídicos.
        for k in range(44):
            if data[k] == 0xFF:
                print(" <-- Este dato es incorrecto.")
                logging.info(" <-- Este dato es incorrecto.")
                correct_set = False
            if data[k] == 0x77:
                print("  <-- Este dato ni siquiera fue modificado con respecto a su valor inicial.")
                logging.info("<-- Este dato ni siquiera fue modificado con respecto a su valor inicial.")
                correct_set = False
        
        # Verificamos si correct_set es False, lo que querría decir que los datos recibidos por el CP son incorrectos o verídicos. 
        if correct_set == False:
            print("Los datos son erróneos. Se procede a descartar la trama de datos.")
            logging.info("Los datos son erróneos. Se procede a descartar la trama de datos.")

        else:
            # Leer el ultimo byte y verificar si es ETX (0x03) ya que es lo que corresponde a lo que se debe recibir como ultimo dato.
            if data[43] != '3':
                print("El final de la trama de datos ETX es diferente al esperado. Se procede a descartar la trama de datos.")
                logging.info("El final de la trama de datos ETX es diferente al esperado. Se procede a descartar la trama de datos.")
            else:
                
                """Esto está calculando el valor decimal de un ID en formato hexadecimal.
                La función int(data[1], 16) convierte el valor hexadecimal almacenado en 
                data[1] a un entero decimal. Luego se resta 48 para ajustar el código ASCII
                al valor real del dígito. Esto se hace para cada dígito hexadecimal del ID
                y se multiplica por la posición correspondiente en la base decimal 
                (1000, 100, 10, 1). Finalmente, se suman estos valores para obtener el ID 
                en formato decimal."""
                ID_H = (int(data[1], 16)-48)*1000 + (int(data[2], 16)-48)*100 + (int(data[3], 16)-48)*10 + int(data[4], 16)-48
                
                """De manera similar, esto calcula el valor decimal del ID, pero teniendo
                en cuenta que está en formato hexadecimal y se trata de un valor de 16 bits.
                La multiplicación y suma siguen el mismo principio explicado anteriormente."""
                ID_D = (int(data[1], 16)-48)*4096 + (int(data[2], 16)-48)*256 + (int(data[3], 16)-48)*16 + int(data[4], 16)-48
                
                """Esto realiza un proceso similar para el campo "CM" (comando). Calcula el
                valor decimal tanto para la parte alta (CM_H) como para la parte baja (CM_D)."""
                CM_H = (int(data[5], 16)-48)*10 + int(data[6], 16)-48
                CM_D = (int(data[5], 16)-48)*16 + int(data[6], 16)-48
                
                """De nuevo, realiza una conversión de hexadecimal a decimal para los campos
                de longitud (LEN_H y LEN_D)."""
                LEN_H = (int(data[7], 16)-48)*10 + int(data[8], 16)-48
                LEN_D = (int(data[7], 16)-48)*16 + int(data[8], 16)-48
                
                if (LEN_D != 16):
                    print("Los datos del conteo de pasajeros no vienen separados en dos grupos de 8 bytes. Se procede a descartar la trama de datos.")
                    logging.info("Los datos del conteo de pasajeros no vienen separados en dos grupos de 8 bytes. Se procede a descartar la trama de datos.")
                else:
                    if (CM_H != 93):
                        print("El comando CM no es 0x39 0x33; no es el valor que se esperaba. Se procede a descartar la trama de datos.")
                        logging.info("El comando CM no es 0x39 0x33; no es el valor que se esperaba. Se procede a descartar la trama de datos.")
                    else:
                        if (LEN_H != 10):
                            print("La longitud LEN no es 0x31 0x30; no es el valor que se esperaba. Se procede a descartar la trama de datos.")
                            logging.info("La longitud LEN no es 0x31 0x30; no es el valor que se esperaba. Se procede a descartar la trama de datos.")
                        else:
                            if (data[25] != '30' or data[26] != '30' or data[27] != '30' or data[28] != '30' or data[29] != '30' or data[30] != '30' or data[31] != '30' or data[32] != '30' or
                                data[33] != '30' or data[34] != '30' or data[35] != '30' or data[36] != '30' or data[37] != '30' or data[38] != '30' or data[39] != '30' or data[40] != '30'):
                                print("El DATA2 está conformado por valores diferentes a 0x30; no es lo que se esperaba. Se procede a descartar la trama de datos.")
                                logging.info("El DATA2 está conformado por valores diferentes a 0x30; no es lo que se esperaba. Se procede a descartar la trama de datos.")
                            else:
                                if (data[9] != '30' or data[10] != '30' or data[11] != '30' or data[12] != '30'):
                                    print("El número de pasajeros que han subido a la unidad sobrepasa la cantidad de 65535 personas. Se procede a descartar la trama de datos.")
                                    logging.info("El número de pasajeros que han subido a la unidad sobrepasa la cantidad de 65535 personas. Se procede a descartar la trama de datos.")
                                else:
                                    if (data[17] != '30' or data[18] != '30' or data[19] != '30' or data[20] != '30'):
                                        print("El número de pasajeros que han subido a la unidad sobrepasa la cantidad de 65535 personas. Se procede a descartar la trama de datos.")
                                        logging.info("El número de pasajeros que han subido a la unidad sobrepasa la cantidad de 65535 personas. Se procede a descartar la trama de datos.")
                                    else:
                                        
                                        """Se calcula el valor real de lo recibido por el CP, ya que el
                                        CP regresa los valores en HEX y se debe de hacer la conversion a
                                        DEC para eso se saca el numero verdadero sumando las posiciones
                                        del 13-16 para la subida (DATA1UP_D) y del 21-24 para la bajada (DATA1DW_D).
                                        """
                                        
                                        """
                                        NOTA: Cuando un valor en HEX es mayor a 39 se le esta restando 48 y ademas 7
                                        al valor decimal para poderlo tener en su valor equivalente en HEX después
                                        de la conversion a DEC.
                                        Por ejemplo: 'int('46',16)' es igual a 70, entonces si le restamos 48 y 7
                                        nos quedaría: 70-48-7=15 que 15 es lo equivalente a F.
                                        """
                                        DATA1UP_D = 0
                                        if data[13] > '39':
                                            DATA1UP_D += (int(data[13],16)-48-7)*4096
                                        else:
                                            DATA1UP_D += (int(data[13],16)-48)*4096
                                            
                                        if data[14] > '39':
                                            DATA1UP_D += (int(data[14],16)-48-7)*256
                                        else:
                                            DATA1UP_D += (int(data[14],16)-48)*256
                                            
                                        if data[15] > '39':
                                            DATA1UP_D += (int(data[15],16)-48-7)*16
                                        else:
                                            DATA1UP_D += (int(data[15],16)-48)*16
                                            
                                        if data[16] > '39':
                                            DATA1UP_D += int(data[16],16)-48-7
                                        else:
                                            DATA1UP_D += int(data[16],16)-48
                                            
                                        DATA1DW_D = 0
                                        if data[21] > '39':
                                            DATA1DW_D += (int(data[21],16)-48-7)*4096
                                        else:
                                            DATA1DW_D += (int(data[21],16)-48)*4096
                                            
                                        if data[22] > '39':
                                            DATA1DW_D += (int(data[22],16)-48-7)*256
                                        else:
                                            DATA1DW_D += (int(data[22],16)-48)*256
                                            
                                        if data[23] > '39':
                                            DATA1DW_D += (int(data[23],16)-48-7)*16
                                        else:
                                            DATA1DW_D += (int(data[23],16)-48)*16
                                            
                                        if data[24] > '39':
                                            DATA1DW_D += int(data[24],16)-48-7
                                        else:
                                            DATA1DW_D += int(data[24],16)-48
                                            
                                        print("DATA UP: ", DATA1UP_D)
                                        print("DATA DOW: ", DATA1DW_D)
                                        logging.info("DATA UP: %s | DATA DOW: %s", DATA1UP_D, DATA1DW_D)
                                        time.sleep(2)
                                        print("Finaliza recepción.")
                                        print("#"*50)
    except Exception as e:
        print(e)
        print("Error en la recepción de datos.")
        logging.info(
            "Error en la recepción de datos. %s", e)
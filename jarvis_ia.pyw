import os
import re
import speech_recognition as sr
import pyttsx3
import ollama

# ---------------------------------------------------------
# Configuración de Sintesis de Voz (Text-to-Speech)
# ---------------------------------------------------------
engine = pyttsx3.init()
engine.setProperty('rate', 175)  # Velocidad de lectura

def hablar(texto):
    """Hace que el asistente hable y muestre el texto en pantalla."""
    print(f"\n🤖 JARVIS: {texto}\n")
    engine.say(texto)
    engine.runAndWait()

# ---------------------------------------------------------
# Historial de Conversación (Memoria del Asistente)
# ---------------------------------------------------------
HISTORIAL_CONVERSACION = [
    {
        "role": "system",
        "content": (
            "Eres JARVIS, un asistente virtual de inteligencia artificial highly competente, elegante y educado, "
            "inspirado en Iron Man. Responde siempre en español de forma concisa, breve y directa al punto "
            "(máximo 2 o 3 oraciones por respuesta) para que sea rápido de escuchar en voz alta."
        )
    }
]

def consultar_ia(mensaje_usuario):
    """Envía el mensaje a la IA local usando Ollama manteniendo el historial."""
    # Añadir el mensaje del usuario al historial
    HISTORIAL_CONVERSACION.append({"role": "user", "content": mensaje_usuario})
    
    try:
        # Llamada a Ollama con el modelo llama3.2 (o phi3)
        response = ollama.chat(model='llama3.2', messages=HISTORIAL_CONVERSACION)
        respuesta_texto = response['message']['content']
        
        # Limpiar emojis o caracteres especiales no deseados en la voz
        respuesta_texto = re.sub(r'[^\w\s,.\xbf\x3f\xa1\x21]', '', respuesta_texto)
        
        # Guardar respuesta en la memoria
        HISTORIAL_CONVERSACION.append({"role": "assistant", "content": respuesta_texto})
        return respuesta_texto
    except Exception as e:
        return f"Lo siento, ocurrió un error al conectar con mi núcleo de IA: {e}"

# ---------------------------------------------------------
# Captura de Audio por Micrófono
# ---------------------------------------------------------
def escuchar():
    """Captura el audio del micrófono y lo convierte a texto."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("[Escuchando...]")
        r.adjust_for_ambient_noise(source, duration=0.4)
        try:
            audio = r.listen(source, timeout=6, phrase_time_limit=8)
            comando = r.recognize_google(audio, language="es-ES")
            print(f"👤 Tú: {comando}")
            return comando
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return ""
        except sr.RequestError:
            print("[Error] Falla en la conexión con el motor de voz.")
            return ""

# ---------------------------------------------------------
# Bucle Principal de Control
# ---------------------------------------------------------
if __name__ == "__main__":
    hablar("Sistemas principales en línea. A su disposición, señor.")
    
    while True:
        texto = escuchar()
        texto_lower = texto.lower()
        
        # Comprobar si se mencionó la palabra clave 'Jarvis'
        if "jarvis" in texto_lower:
            # Eliminar la palabra 'jarvis' de la instrucción si viene junta (ej: "Jarvis qué es Python")
            instruccion = re.sub(r'\bjarvis\b', '', texto, flags=re.IGNORECASE).strip()
            
            # Si solo dijo "Jarvis", pedir la instrucción
            if not instruccion:
                hablar("¿Sí, señor? Le escucho.")
                instruccion = escuchar()
            
            if instruccion:
                # Caso de salida
                if "desactivar" in instruccion.lower() or "adiós" in instruccion.lower():
                    hablar("Entendido. Desactivando protocolos. Tenga un buen día.")
                    break
                
                # Procesar cualquier instrucción aleatoria o conversación con la IA
                respuesta = consultar_ia(instruccion)
                hablar(respuesta)
import os
import json

# Lista de fuentes (extraída del notebook_get anterior)
SOURCES = [
    ["69c9e25f-f55e-4995-a8dc-ce468ead52fa", "14 Consejos Para Corregir el Insomnio en 77 Minutos."],
    ["7d16acb5-51f6-41ed-8936-cfaa84e8ab42", "ALIMENTOS TOXICOS PARA EL CEREBRO HUMANO"],
    ["e7cdfd00-980e-4cec-8ad7-177300c8ab53", "Así Tripliqué mi Testosterona (Paso a paso)"],
    ["9232a754-25a4-4a39-a432-93014d4d2444", "Ayuno de Dopamina: Resetea tu cerebro y haz los cambios difíciles | Dr. La Rosa"],
    ["e5f0724a-25cb-4b19-9893-861a961f7231", "BAJA TU INFLAMACION HACIENDO ESTO"],
    ["ee91cf9f-426d-4fa7-95b8-e52cc6502fa8", "COMO ELIMINAR CANDIDA DE TU ORGANISMO NATURALMENTE"],
    ["04f8e55f-19ba-4478-bb74-79da739e1203", "Como LIMPIAR EL HÍGADO naturalmente (HÍGADO GRASO)"],
    ["07f7b0b1-42a4-42d5-b428-eac5242e8331", "Como usar el Magnesio para frenar tu Envejecimiento y Prevenir Infartos"],
    ["42a80ec8-51f8-486c-ab03-c60ce9107350", "Cuánta Agua Tomar, Cómo Evitar Levantarte a Orinar y TODO Sobre Hidratación."],
    ["7d4d71ec-2eab-49ad-a5fe-6076ee3559cd", "Cuántas horas de sueño mejoran nuestra salud - ft. Nico Fernandez Miranda"],
    ["ba6c1204-8409-4223-9c3c-0013132346e3", "Cuánto tienes que Caminar para Perder Grasa y Vivir más?"],
    ["7979bb98-3858-40c7-a84a-81f2db6c2372", "CÓMO LIMPIAR EL COLON NATURALMENTE"],
    ["e94a9596-f925-4827-9227-7b7a98c87922", "Cómo Afectan los Lácteos a tu Longevidad"],
    ["7f10971b-fdc0-4935-8f9e-2dc5e4062c8d", "Cómo Aumentar Tu TESTOSTERONA Naturalmente"],
    ["c82640e6-0b0d-48d4-93cc-ff05057fbc66", "Cómo Cambiar tus Malos Hábitos"],
    ["f0395a86-4e74-433c-b1a9-3c2f79e3f163", "Cómo Evitar un Infarto"],
    ["772be40a-b03f-4cea-85ee-e6422423b37d", "Cómo Funciona tu Erección y como Potenciarla"],
    ["8fe8c5c3-64e5-4ab5-a1ec-44552f3266d2", "Cómo Organizar tu Día Para Estar Más Sano"],
    ["d0245f15-188b-499b-ba7a-b5ffc821c0a1", "Cómo REPARAR tu MICROBIOTA (Paso a Paso)"],
    ["6e6a3036-6fce-4ebb-8842-6840935143f9", "Cómo REPARAR tu SUEÑO de manera EFICIENTE"],
    ["555c87de-bec9-4681-85c4-b4872781f946", "Cómo Reducir la Hipertensión Naturalmente"],
    ["2366b43f-3364-4188-8510-8a8cc49b9829", "Cómo Reparar tu Digestión y tus Intestinos Paso a Paso"],
    ["7a7fe3e7-a6a0-45ce-8827-fee23378bf31", "Cómo aumentar tus CELULAS MADRE naturalmente (Rejuvenecimiento)"],
    ["cdfc208c-d908-4ce4-b8b9-3275941a4721", "Cómo el Ayuno Daña Unas Hormonas y Mejora Otras"],
    ["b3d44146-4d18-40ca-92f6-b9d403feff2f", "Dime donde acumulas grasa y te diré que hormona lo causa"],
    ["76be7740-28ce-42f1-b858-149b6e6e767f", "ELEMENTOS que CAUSAN nuestro SOBREPESO"],
    ["9c6e7df0-ae4d-40e5-8207-45728160ddeb", "El Ejercicio Ideal para Vivir Más"],
    ["674ee31b-486b-4b98-8142-f3fe1f4a36e6", "El PEOR HORARIO para COMER (Y el mejor)"],
    ["c11e7824-74a5-4b9d-8d8a-5a4e803f985d", "El Plan de Ejercicio Más Eficiente para Vivir Más"],
    ["f42808ae-d119-468f-a7ec-ca18106f52f3", "Elimina la Celulitis de Forma Natural"],
    ["c0345495-5cbb-4ef6-86d5-2e86a391a53d", "Estas Sustancias Te Hacen Más INTELIGENTE"],
    ["ccfea137-5b0f-4c80-ab9f-bc287225cb00", "Este Entrenamiento Fortalece Tus Articulaciones"],
    ["b884cf28-c20e-4791-a63d-7e0f94902cd0", "Esto Destruye Tu Colágeno Y Te Hace Envejecer"],
    ["3ab79130-b33b-4e57-826d-64beb8a43529", "Estos Cambios Mejoran Tu Imagen"],
    ["03882aaa-c285-47ba-9564-eef6cd444491", "Estos Productos Dañan Tu Salud, Tu Fertilidad y Tus Hormonas"],
    ["fc201079-ec2e-4cc6-9ebe-b0a467f80957", "Estos consejos te dan más Disciplina"],
    ["bea69620-9cdb-4b2b-b01f-c573dc05d9e2", "Guía Para Perder Grasa y Ganar Músculo"],
    ["411f1a9a-bd65-4f22-9425-200e80b10499", "Las 5 Sustancias que FRENAN el ENVEJECIMIENTO"],
    ["0378c7f4-7987-462c-a6ca-46227d909f49", "Las estrategias más EFECTIVAS para vivir más y mejor"],
    ["8d9571a1-953e-49da-8bbb-736e40005093", "Llevamos años desarrollando esto para vos"],
    ["61638a80-0a90-4006-8507-dd54f6e874f9", "Mejora Tu Visión"],
    ["b229fb24-e6da-44e6-92af-1719bb70ece5", "Melena de león, reishi, cordyceps: qué le hacen a tu cerebro"],
    ["03c98758-dca4-4135-b421-9ce785a4d820", "Necesitamos Comer Menos Sal?"],
    ["ec74bba9-fe33-4055-bae5-cf4a54c474c6", "Por qué Perdemos Pelo y Cómo Frenarlo"],
    ["99791530-6409-479b-adc9-f488e4dfd547", "Por qué el AYUNO DEJA de FUNCIONAR"],
    ["34b384bf-198b-4861-82ad-520d1341d55d", "REPARA tu PIEL con Estos Consejos"],
    ["4e865cb4-e16d-4f41-9f97-64924e6a1096", "Rutinas Basadas en Evidencia Para Mejorar tu Piel"],
    ["6e302cc8-ba67-4447-8c85-d2d555e99ce6", "TU BELLEZA DEPENDE DE TUS HÁBITOS, no de tus genes"],
    ["9c2fff60-7386-491e-a0d5-e385ed391e1e", "Todo lo que necesitas para reparar tus INTESTINOS"],
    ["a8dad9f9-a849-42f3-9ed8-25ff271d80f2", "Todo lo que te Impide Ganar Músculo"],
    ["aff53778-8f0b-498b-bc53-ac69ead5ff76", "¿Cómo tener una PIEL SIN ACNÉ ni FLACIDEZ?"],
    ["ce1c0216-b879-4621-b066-2cd586b34c80", "¿POR QUÉ tu TESTOSTERONA está BAJANDO?"],
    ["14a4e260-7889-49c5-8fa7-ad23449427fe", "¿Qué Sucede si no Consumimos Omega 3?"],
    ["bce20f74-8c24-4eba-8772-0310931b1ddf", "¿Qué nos hace estar cada vez mas cansados?"],
    ["e9e5f968-47d1-452a-8771-eb6bad04eaa1", "¿Vale la pena Estirar?"]
]

MASTER_FILE = "d:/YOP/BioAgent/TRANSCRIPCIONES_MAESTRAS.md"

def main():
    with open(MASTER_FILE, "w", encoding="utf-8") as f:
        f.write("# TRANSCRIPCIONES MAESTRAS - RUTINA ESTRATÉGICA\n\n")
        f.write("Este documento contiene el conocimiento crudo de 56 fuentes de salud del Dr. La Rosa.\n\n---\n\n")

    print(f"Iniciando consolidación en {MASTER_FILE}")
    # En este paso, el agente usará source_get_content secuencialmente. 
    # El script servirá de guía para no olvidar ninguna fuente.

if __name__ == "__main__":
    main()

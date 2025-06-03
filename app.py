from flask import Flask, render_template, request, redirect
import xml.etree.ElementTree as ET

from pypmml import Model

app = Flask(__name__)

def leer_variables_desde_pmml(ruta_pmml):
    tree = ET.parse(ruta_pmml)
    root = tree.getroot()

    namespace_uri = root.tag[root.tag.find("{")+1:root.tag.find("}")]
    ns = {'pmml': namespace_uri}

    data_fields = root.findall('.//pmml:DataField', ns)
    variables = {}
    rangos = {}

    for field in data_fields:
        nombre = field.attrib.get('name')
        valores = [v.attrib['value'] for v in field.findall('pmml:Value', ns)]
        interval = field.find('pmml:Interval', ns)

        if interval is not None:
            left = interval.attrib.get('leftMargin')
            right = interval.attrib.get('rightMargin')
            rangos[nombre] = (left, right)
        else:
            rangos[nombre] = None

        variables[nombre] = valores if valores else None
   
    return variables, rangos

@app.route("/", methods=["GET", "POST"])
def index():
    ruta_pmml = "enfermedad_renal.pmml"
    variables, rangos = leer_variables_desde_pmml(ruta_pmml)
    datos_ingresados = {}
    mensaje = ""

    modelo = Model.load(ruta_pmml)

    if request.method == "POST":
        for var in variables:
            datos_ingresados[var] = request.form.get(var)

      
        resultado = modelo.predict(datos_ingresados)
 
        clase_predicha = resultado['predicted_' + modelo.targetName]

        if clase_predicha == 'enfermo':
            mensaje = "Predicción: el paciente PUEDE adquirir enfermedad renal crónica."
        elif clase_predicha == 'sano':
            mensaje = "Predicción: el paciente NO tiene riesgo de adquirir enfermedad renal crónica."
        else:
            mensaje = f"El paciente puede estar: {clase_predicha}"

    return render_template("index.html", variables=variables, datos=datos_ingresados, mensaje=mensaje, rangos=rangos)


if __name__ == "__main__": 
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
    #app.run()

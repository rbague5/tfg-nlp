#!/usr/bin/env python
# coding: utf8
"""Example of training an additional entity type

This script shows how to add a new entity type to an existing pretrained NER
model. To keep the example short and simple, only four sentences are provided
as examples. In practice, you'll need many more — a few hundred would be a
good start. You will also likely need to mix in examples of other entity
types, which might be obtained by running the entity recognizer over unlabelled
sentences, and adding their annotations to the training set.

The actual training is performed by looping over the examples, and calling
`nlp.entity.update()`. The `update()` method steps through the words of the
input. At each word, it makes a prediction. It then consults the annotations
provided on the GoldParse instance, to see whether it was right. If it was
wrong, it adjusts its weights so that the correct action will score higher
next time.

After training your model, you can save it to a directory. We recommend
wrapping models as Python packages, for ease of deployment.

For more details, see the documentation:
* Training: https://spacy.io/usage/training
* NER: https://spacy.io/usage/linguistic-features#named-entities

Compatible with: spaCy v2.1.0+
Last tested with: v2.1.0
"""
from __future__ import unicode_literals, print_function

import plac
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding
import os.path
from datetime import datetime
from labeler_and_converter_of_data.ConvertSpacyTrainData import convert_data

# training data
# Note: If you're using an existing model, make sure to mix in examples of
# other entity types that spaCy correctly recognized before. Otherwise, your
# model might learn the new type, but "forget" what it previously knew.
# https://explosion.ai/blog/pseudo-rehearsal-catastrophic-forgetting
TRAIN_DATA = convert_data("data_blank.json")
print(type(TRAIN_DATA))

@plac.annotations(
    model=("Model name. Defaults to blank 'es' model.", "option", "m", str),
    new_model_name=("New model name for model meta.", "option", "nm", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int),
)
def main(model=None, new_model_name="FECHA", output_dir="./blank_model", n_iter=100):
    """Set up the pipeline and entity recognizer, and train the new entity."""
    random.seed(0)

    nlp = spacy.blank("es")  # create blank Language class
    print("Created blank 'es' model")
    # Add entity recognizer to model if it's not in the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner)
    # otherwise, get it, so we can add labels to it
    else:
        ner = nlp.get_pipe("ner")

    # new entity label
    LABEL = "FECHA"
    ner.add_label(LABEL)  # add new entity label to entity recognizer

    if model is None:
        print("Begin training")
        optimizer = nlp.begin_training()
    else:
        print("Resume training")
        optimizer = nlp.resume_training()
    move_names = list(ner.move_names)
    print(f"Move names: {move_names}")

    # get names of other pipes to disable them during training
    pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
    print(f"Other pipes: {other_pipes}")

    with nlp.disable_pipes(*other_pipes):  # only train NER
        enabled_pipes = nlp.pipe_names
        print(f"Enabled pipes: {enabled_pipes}")

        sizes = compounding(1.0, 4.0, 1.001)

        configuration = nlp.entity.cfg
        print(f"configuration: {configuration}")

        total_loses = list()
        total_iterations = list()
        # batch up the examples using spaCy's minibatch
        for itn in range(n_iter):
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print(f"[{current_time}] Starting iteration: {itn}/{n_iter}")
            random.shuffle(TRAIN_DATA)
            batches = minibatch(TRAIN_DATA, size=sizes)
            losses = {}
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, sgd=optimizer, drop=0.20, losses=losses)
            print(f"          Losses {losses}")
            total_loses.append(losses)

            print(f"Total Iterations: {total_iterations}")
            print(f"Total Losses: {total_loses}")
            print()
        print("[")
        for x, y in zip(total_iterations, total_loses):
            print("{'iteration':" + str(x) + "," + str(y)[1:] + ",")
        print("]")

    # test the trained model
    test_text = 'Roj: STS 5753/2016 - ECLI: ES:TS:2016:5753 Id Cendoj: 28079140012016101021 Órgano: Tribunal Supremo. Sala de lo Social Sede: Madrid Sección: 1 Fecha: 07/12/2016 Nº de Recurso: 1599/2015 Nº de Resolución: 1043/2016 Procedimiento: Social Ponente: MARIA LOURDES ARASTEY SAHUN Tipo de Resolución: Sentencia Resoluciones del caso: STSJ PV 3532/2014, STS 5753/2016 "SENTENCIA En Madrid, a 7 de diciembre de 2016 Esta sala ha visto el recurso de casación para la unificación de doctrina interpuesto por Dª Constanza , representada y asistida por el letrado D. Héctor Mata Diestro, contra la sentencia dictada el 13 de noviembre de 2014 por la Sala de lo Social del Tribunal Superior de Justicia del País Vasco, en recurso de suplicación nº 1965/14 , interpuesto contra la sentencia de fecha 26 de junio de 2014, dictada por el Juzgado de lo Social nº 1 de Vitoria , en autos núm. 134/2014, seguidos a instancias de Dª Constanza , contra Lampsys Light Systems S.L. Ha sido parte recurrida Lampsys Light Systems S.L. representado y asistido por la letrada Dª. Elbire Corral Fernández de Zuazo Ha sido ponente la Excma. Sra. D.ª Maria Lourdes Arastey Sahun ANTECEDENTES DE HECHO PRIMERO.- Con fecha 26 de junio de 2014 el Juzgado de lo Social nº 1 de Vitoria dictó sentencia , en la que se declararon probados los siguientes hechos: « 1º .- La actora Doña Constanza , viene prestando servicios para la empresa LAMPSYS LIGHT SYSTEMS SL, con una antigüedad de 4 de marzo de 2009, categoría profesional de grupo 3, y salario bruto mensual de 1.406,18 euros con prorrata de pagas extras. 2º.- La demandante ha sido delegada de personal por el sindicato ELA desde el 23 de noviembre de 2012 siendo también delegadas Doña Rebeca por el mismo sindicato, y otra trabajadora por el sindicato CCOO. 3º.- Los trabajadores de la empresa comunicaron a la oficina pública de elecciones sindicales del departamento de Justicia, Trabajo y Seguridad Social del Gobierno Vasco el 18 de junio de 2013 la convocatoria de una asamblea de trabajadores a celebrar el 1 de julio de 2013 con el objeto de revocar a las delegadas de personal Doña Constanza y Doña Rebeca , siendo las mismas revocadas en su cargo tras la votación de la plantilla en la asamblea celebrada el 1 de julio de 2013. 4º.- La demandante siempre ha desempeñado funciones correspondientes al grupo 2, si bien por decisión de la empresa se le reconoció el grupo 3, aunque nunca ha realizado funciones correspondientes a dicho grupo. 5º.- La demandante ha presentado demanda contra la empresa en el año 2012 reclamando el derecho a percibir un complemento de antigüedad que fue reconocido extrajudicialmente por la empresa el 5 de junio de 2012, reclamó igualmente por escrito a la empresa juntamente con otros cuatro trabajadores que la empresa faltaba al pago de los salarios de forma reiterada desde el mes de julio de 2011, presentando con otros trabajadores denuncia ante la Inspección de Trabajo por impago de salarios el 14 de mayo de 2012, asimismo presentó denuncia ante la Inspección de Trabajo con otros trabajadores por las temperaturas en la planta de producción, no constando en las actuaciones ningún informe de la Inspección de Trabajo relativo a dichas denuncias, ni demanda judicial. 6º.- El 7 de marzo de 2013 por parte de la demandante y la otra delegada sindical de ELA se comunicó la convocatoria de huelga que tendría su inicio a partir de las 00:00 horas del día 14 de marzo de 2013, siendo la demandante uno de los miembros del Comité de Huelga, que pasó de estar prevista inicialmente para unos días a ser declarada huelga indefinida, y posteriormente a partir del 1 de agosto de 2013 huelga parcial y a partir del 1 de enero de 2014 huelga de una hora de duración. 7º .- La demandante juntamente con la otra delegada de ELA presentaron varias denuncias ante la Inspección de trabajo relacionadas con la huelga obrando en las actuaciones informe de la Inspección de Trabajo folios 298 a 305 de las actuaciones, presentando el sindicato ELA demanda por vulneración del derecho de huelga, así como al abono de una indemnización de 30.000 euros, cuyo conocimiento correspondió al Juzgado de lo Social n° 4 de Vitoria (autos n° 448/13) que en fecha 10 de febrero de 2014 dictó sentencia desestimando íntegramente la demanda. Obra copia de dicha sentencia en los folios 280 a 294 de las actuaciones. 8º .- Los trabajadores no huelguistas presentaron escrito ante la Inspección de Trabajo en fecha 23 de mayo de 2013 quejándose de las presiones ejercidas por el Comité de Huelga, celebrándose en fecha 18 de julio de 2013 reunión entre la representación legal de los trabajadores y la empresa en la que se pone de manifiesto quejas sobre la postura de la empresa ante la huelga, reiterando la empresa su compromiso y pidiendo disculpas por la situación aunque no se considera responsable de las acciones que realicen algunos huelguistas. 9º .- El 23 de julio de 2012 se comunicó por la empresa que previendo una bajada de los pedidos de clientes siendo habitual que esto suceda dado que el mercado de la motocicleta se concentra especialmente entre febrero y junio se reorganizaran los recursos y a partir del 3 de septiembre y hasta nueva orden se trabajará solo en turno de mañana de 6:00 a 14:15 horas. 10º .-En el año 2013 la empresa inició el año con dos turnos, pasándose después a un solo turno. 11º .-Obran en las actuaciones los bonos de trabajo de la actora desde en el periodo 2012-2013 cuyo contenido se da por reproducido a efectos de su incorporación a los hechos probados. 12º .-La actora durante el año 2012 y 2013 ha prestado servicios en las tres secciones de la empresa inyección, metalizado, y montaje, con predominio en la sección de metalizado. 13º .- En la sección de metalizado prestan servicios otros trabajadores de la empresa obrando en las actuaciones los bonos de trabajo del periodo 2012-2013. 14º .-La mayor parte de los trabajadores de la empresa son polivalentes, prestando servicios en diferentes secciones. 15º .-La trabajadora Doña Delia que trabaja en la sección de metalizado está encuadrada en el grupo 2. 16º .-Con fecha 15 de enero de 2013 se comunicó a la actora que a partir del 30 de enero de 2013 se incorporará al régimen de trabajo a turnos rotatorios con el siguiente horario. Turno 1 de 6 a 14;15 ( 15 minutos de descanso bocadillo). Turno 2 De 8:30 a 16:45 (15 minutos de descanso bocadillo). Se indica que no se descarta volver al horario anterior sin estar a turnos dependiendo de la evolución de la coyuntura económica y de mercado. Se incorpora a la trabajadora a la sección de metalizados. Obra copia de dicho escrito en los folios 295 y 296. 17º.- El 28 de febrero de 2014 se comunica a la trabajadora por escrito que a partir del 17 de marzo se incorporará al régimen de trabajo a turnos rotatorios con el siguiente horario. Turno 1 de 6 a 14;15 ( 15 minutos de descanso bocadillo). Turno 2 De 8:30 a 16:45 (15 minutos de descanso bocadillo). Se indica que se incorporará a la sección de metalizado. Obra copia de dicho escrito en los folios 293 y 294 de las actuaciones. 18º .-Es de aplicación el Convenio de la Industria química.». En dicha sentencia aparece la siguiente parte dispositiva: «Que desestimando la demanda formulada por Doña Constanza , contra la empresa LAMPSYS LIGHT SYSTEMS SL, debo absolver y absuelvo a la demandada de las pretensiones deducidas en su contra». SEGUNDO.- La citada sentencia fue recurrida en suplicación por Dª Constanza ante la Sala de lo Social del Tribunal Superior de Justicia del País Vasco, la cual dictó sentencia en fecha 13 de noviembre de 2014 , en la que consta el siguiente fallo: «Que declaramos la nulidad de las actuaciones practicadas desde la presentación del Recurso de Suplicación por DOÑA Constanza frente a la Sentencia de 26 de Junio de 2014, del Juzgado de lo Social nº 1 de Gastéiz , en autos nº 134/14, declarando la firmeza de la referida Sentencia». TERCERO.- Por la representación de Dª Constanza se formalizó el presente recurso de casación para la unificación de doctrina ante la misma Sala de suplicación. A los efectos de sostener la concurrencia de la contradicción exigida por el art. 219.1 de la Ley Reguladora de la Jurisdicción Social (LRJS ), la recurrente propone, como sentencia de contraste, la dictada por la Sala de lo Social del Tribunal Superior de Justicia del País Vasco de 25 de febrero de 2014, (rec. 46/2014 ). CUARTO.- Por providencia de esta Sala de fecha 14 de octubre de 2015 se admitió a trámite el presente recurso y se dio traslado del escrito de interposición y de los autos a la representación procesal de la parte recurrida para que formalice su impugnación en el plazo de quince días . Evacuado el traslado de impugnación, se pasaron las actuaciones al Ministerio Fiscal que emitió informe en el sentido de considerar el recurso improcedente. QUINTO.- Instruida la Excma. Sra. Magistrada Ponente, se declararon conclusos los autos, señalándose para votación y fallo el día 22 de noviembre de 2016, fecha en que tuvo lugar. FUNDAMENTOS DE DERECHO PRIMERO.- 1. La sentencia recurrida niega que la sentencia del Juzgado de lo social nº 1 de los de Vitoria- Gasteiz pudiera ser recurrible en suplicación por considerar que el pleito tiene por objeto la impugnación de una modificación sustancial de condiciones de trabajo de carácter individual y, en consecuencia, se tramitó por el art. 138 LRJS . Rechaza la Sala vasca que la pretensión de que se declare que con dicha modificación se ha producido una vulneración de derechos fundamentales y que, en consecuencia, se condene a la parte demandada a la indemnización de daños y perjuicios en cuantía de 8000 ? no comporta la posibilidad de acceder a la suplicación, al entender excluyente de tal recuso la remisión del art. 184 LRJS . 2. La sentencia del Juzgado de instancia había desestimado la demanda, por lo que es la trabajadora quien acude ahora a la casación para unificación de doctrina aportando, como sentencia de contraste, la dictada por la misma Sala del País Vasco el 25 de febrero de 2014 (rollo 46/2014 ) que, en efecto, entendió que la invocación de lesión de derechos fundamentales altera la cuestión de la recurribilidad. Es evidente que la formalización del recurso de casación unificadora ha de realizarse cumpliendo los presupuestos del artículo 219 LRJS respecto de la contradicción entre sentencias. No obstante, dado que la admisibilidad o no del recurso de suplicación incide sobre la eventual competencia, no sólo del Tribunal Superior de Justicia, sino de esta Sala IV del Tribunal Supremo, pues nuestro enjuiciamiento, en vía de casacón unificadora, va a depender de que la Sala de suplicación tuviera competencia para pronunciarse en el litigio y ésta, a su vez, está vinculada a la recurribilidad de la sentencia del Juzgado de origen, no es necesario el análisis de la contradicción del art. 219.1 LRJS ya que la cuestión de la competencia puede ser analizada de oficio y ello, pues, con independencia de las alegaciones de las partes. Como hemos reiterado, «ello es así porque este recurso unificador únicamente procede contra las sentencias dictadas en suplicación, lo que supone que la recurribilidad en casación se condiciona a que la sentencia de instancia fuera, a su vez, recurrible en suplicación y por ello el control de la competencia funcional de la Sala supone el control sobre la procedencia o improcedencia de la suplicación...» (entre otras, SSTS/4ª de 12 y 14 mayo 2015 - rcuds. 2664/2014 y 82/2014-; y 5 mayo y 2 junio 2016 - 3494/2014 y 3820/2014 -). SEGUNDO.- 1. En relación con el acceso al recurso de las sentencias que dan respuesta a procesos seguidos por el cauce del art. 138 LRJS , esta Sala se ha pronunciado ya sobre la posibilidad de acceso al recurso de las impugnaciones individuales de modificaciones sustanciales de condiciones de trabajo cuando éstas tengan carácter colectivo (así, STS/4ª de 22 enero y 9 abril 2014 - rcuds. 690/2013 y 949/2013, respectivamente- y,                                         a sensu contrario, 20 julio 2015 -rcud. 1567/2014 -). 2. También la cuestión que ahora se nos suscita ha sido ya objeto de análisis por nuestra parte. En la STS/4ª de 10 marzo 2016 (rcud. 1887/2014 ) abordábamos la cuestión de la acumulación de reclamación de daños y perjuicios -en cuantía superior a 3000 ?- en la impugnación de una modificación sustancial de las condiciones de trabajo, de cambio de puesto de trabajo, en la que se alegaba por el demandante una situación discriminatoria y de persecución, por su condición de representante de los trabajadores. Tras analizar allí los arts. 191 y 192 LRJS y señalando, además, que la acción de acumulación indemnizatoria estaba fundada en una tutela resarcitoria por violación de derechos fundamentales, sosteníamos la recurribilidad de la sentencia. Aun cuando parecía ponerse el acento en la cuestión de la superación de la cuantía, seguíamos así la misma doctrina que ya habíamos instaurado en la STS/4ª de 10 de diciembre de 1999 (rcud. 517/1999 ), en relación a la acumulación de acciones de tutela de derechos fundamentales, y que plasmábamos en la STS/4ª de 3 noviembre 2015 (rcud. 2753/2014 ), respecto de la modalidad procesal propia de la fijación del periodo de disfrute de vacaciones en que, igualmente, se invocaba la tutela de derechos fundamentales, en la que se ponía de relieve el tenor de la remisión procedimental del art. 184 LRJS . 3. Sucede, además, que la STS/4ª de 22 junio 2016 (rcud. 399/2015 ) examina precisamente un supuesto con el cual no cabría mayor analogía, dado que se trataba allí de la demanda de una trabajadora de la misma empresa, también delegada de personal por el mismo sindicato que la actora y en relación a los mismos hechos -como así consta en los ordinales segundo y séptimo del relato de hechos probados de la sentencia de instancia de este caso, que hemos reproducido en los Antecedentes de Hecho-. Siguiendo la misma línea doctrinal que hemos resumido en el apartado anterior, esta última sentencia afirma la recurribilidad de la sentencia. La congruencia con ese criterio se torna aquí doblemente imperativa, dada la identidad de debate jurídico y de supuestos fácticos ya resueltos. Debemos destacar, además, que la postura de esta Sala IV del Tribunal Supremo resulta coincidente con el análisis que, con posterioridad y corroborando la indicada jurisprudencia, se hace en la STC 149/2016, de 16 de septiembre . En ella, dando respuesta a un recurso de amparo, pone de relieve que la remisión que se hace a la modalidad procesal en el precepto de la de tutela de derechos fundamentales no puede comportar inferiores garantías que las que se otorgan en el marco procesal propio de los derechos fundamentales. TERCERO.- 1. Lo expuesto nos lleva a la estimación del recurso y, en consecuencia, casamos y anulamos la sentencia recurrida, debiendo ordenarse la devolución de las actuaciones a la Sala de remisión para que, partiendo de la admisibilidad del recurso, dicte sentencia resolviendo los motivos que el mismo planteaba. 2. De conformidad con lo dispuesto en el art. 235.1 LRJS , no procede la imposición de costas. FALLO Por todo lo expuesto, en nombre del Rey, por la autoridad que le confiere la Constitución, esta sala ha decidido Estimar el recurso de casación interpuesto por Dª Constanza contra la sentencia dictada el 13 de noviembre de 2014 por la Sala de lo Social del Tribunal Superior de Justicia del País Vasco, en recurso de suplicación nº 1965/14 , interpuesto contra la sentencia de fecha 26 de junio de 2014, dictada por el Juzgado de lo Social nº 1 de Vitoria , en autos núm. 134/2014, seguidos a instancias de Dª Constanza , contra Lampsys Light Systems S.L. Casar y anular la citada sentencia y, resolviendo el debate suscitado en suplicación, anulamos la sentencia dictada por el Tribunal Superior de Justicia del País Vasco y acordamos la devolución de las actuaciones a dicho Tribunal a fin de que proceda a dictar sentencia que de resolución a las cuestiones que fueron planteadas en el recurso de suplicación. Sin costas. Notifíquese esta resolución a las partes e insértese en la coleccion legislativa. Así se acuerda y firma. PUBLICACIÓN.- En el mismo día de la fecha fue leída y publicada la anterior sentencia por la Excma. Sra. Magistrada Dª Maria Lourdes Arastey Sahun hallándose celebrando Audiencia Pública la Sala de lo Social del Tribunal Supremo, de lo que como Letrada de la Administración de Justicia de la misma, certifico.'
    doc = nlp(test_text)
    print("Entities in '%s'" % test_text)
    for ent in doc.ents:
        print(ent.label_, ent.text)

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.meta["name"] = new_model_name  # rename model
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        # Check the classes have loaded back consistently
        assert nlp2.get_pipe("ner").move_names == move_names
        doc2 = nlp2(test_text)
        for ent in doc2.ents:
            print(ent.label_, ent.text)


if __name__ == "__main__":
    plac.call(main)
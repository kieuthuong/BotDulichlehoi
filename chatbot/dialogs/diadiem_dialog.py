# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from datatypes_date_time.timex import Timex

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory
from botbuilder.schema import InputHints
from .cancel_and_help_dialog import CancelAndHelpDialog
from .date_resolver_dialog import DateResolverDialog


class DiadiemDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(DiadiemDialog, self).__init__(dialog_id or DiadiemDialog.__name__)

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(DateResolverDialog(DateResolverDialog.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.destination_step,
                ],
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__

    async def destination_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        lehoi_details = step_context.options
        if not lehoi_details.diaDiem:
            return await step_context.end_dialog()
        # lehoi_details.diaDiem = step_context.result
        import rdfextras
        rdfextras.registerplugins()
        # filename = "fesivalVietNam.owl" 
        filename = "fesivalVietNam.owl"
        import rdflib
        g = rdflib.Graph()

        result = g.parse(filename, format='xml')
        # print(result)
        query = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>    
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>   
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>    
        PREFIX xml: <http://www.w3.org/XML/1998/namespace>  
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX :<http://www.semanticweb.org/admin/ontologies/2020/2/untitled-ontology-5#> 

        SELECT DISTINCT ?name
        WHERE 
        { 
        ?x :tenLeHoi ?name.
        ?x :coHoatDong ?act.
        ?x :toChucTai ?loc.
        ?loc :tenDiaDiem ?nloc.
        FILTER( regex(?nloc,"diaDiem","i")) 
        }

        """
        query=query.replace("diaDiem",lehoi_details.diaDiem)
        count=0
        for row in g.query(query):
            fes="%s" % row
            loc=[]
            query1 = """
            PREFIX owl: <http://www.w3.org/2002/07/owl#>    
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>   
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>    
            PREFIX xml: <http://www.w3.org/XML/1998/namespace>  
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX :<http://www.semanticweb.org/admin/ontologies/2020/2/untitled-ontology-5#> 

            SELECT DISTINCT ?nloc
            WHERE 
            { 
            ?x :tenLeHoi ?name.
            ?x :toChucTai ?loc.
            ?loc :tenDiaDiem ?nloc.
            FILTER( regex(?name,"fes","i") ) 
            }

            """
            query1=query1.replace("fes",fes)
            get_text = fes+" t??? ch???c t???i "
            for row in g.query(query1):
                a="%s" % row
                for x in loc:
                    if a==x:
                        break
                loc.append(a)
            for x in loc:
                get_text += x 
                get_text += " "
            get_message = MessageFactory.text(
            get_text, get_text, InputHints.ignoring_input
                )
            await step_context.context.send_activity(get_message)
            loc.clear()
            count+=1
        if count==0:
            get_text = "Ch??a t??m th???y l??? h???i n??o ??? " + lehoi_details.diaDiem
            get_message = MessageFactory.text(
            get_text, get_text, InputHints.ignoring_input
                    )
            await step_context.context.send_activity(get_message)
            return await step_context.next(None)
            # return await step_context.next(next(dantoc_details.danToc))
        return await step_context.next(None)


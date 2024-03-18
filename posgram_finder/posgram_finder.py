import json
import stanza
from stanza.pipeline.core import DownloadMethod

class PosgramFinder:
    def __init__(self, lower_percentage_limit=5):
      with open("model_precontext.txt") as f1:  self.osakaalud_ees=json.load(f1)
      with open("model_postcontext.txt") as f1: self.osakaalud_taga=json.load(f1)
      self.protsendipiir=lower_percentage_limit
      self.nlp=stanza.Pipeline(lang="et", processors="tokenize,pos", download_method=DownloadMethod.REUSE_RESOURCES)

    def posgram_errors(self, text):
        dok=self.nlp(text)
        vastus=[]
        for lause in dok.sentences:
           kolmikud=[]
           jada="".join([sona.xpos for sona in lause.words])+"$"
           koht=0
           print("^"+jada)
           while koht<len(jada)-2:
            if jada[koht]!='Z':
             abi=koht
             kolmik=""
             while len(kolmik)<3 and abi<len(jada)-1:
                if jada[abi]!='Z':
                  kolmik+=jada[abi]
                abi+=1
             kolmikuots=abi
             if len(kolmik)==3:
                while jada[abi]=="Z": abi+=1
                taga=jada[abi]
                otsakoht=abi+1
                abi=koht-1                
                while abi>=0 and jada[abi]=='Z': abi-=1
                if abi>=0: 
                    ees=jada[abi]
                    alguskoht=abi
                else: 
                    ees="^"
                    alguskoht=0
                kommentaar="-"
                eesprotsent=0
                if kolmik in self.osakaalud_ees:
                    if ees in self.osakaalud_ees[kolmik]:
                        eesprotsent=self.osakaalud_ees[kolmik][ees][1]
                    else:
                        kommentaar+=" puuduv eeskontekst"
                else:
                    kommentaar+=" puuduv eeskonteksti kolmik"  
                kolmikud.append([alguskoht, kolmikuots, eesprotsent<self.protsendipiir, kolmik, "ees", ees, eesprotsent, kommentaar])                  
                kommentaar="-"
                tagaprotsent=0
                if kolmik in self.osakaalud_taga:
                    if taga in self.osakaalud_taga[kolmik]:
                        tagaprotsent=self.osakaalud_taga[kolmik][taga][1]
                    else:
                        kommentaar+=" puuduv tagakontekst"
                else:
                    kommentaar+=" puuduv taga kolmik"                    
                kolmikud.append([koht, otsakoht, tagaprotsent<self.protsendipiir, kolmik, "taga", taga, tagaprotsent, kommentaar])                  

            koht+=1
           kolmikud=list(filter(lambda kolmik: kolmik[2], kolmikud))
           kandidaadid=[]           
           for kolmik in kolmikud:
              kandidaat={
                 "value":" ".join([sona.text for sona in lause.words[kolmik[0]:kolmik[1]]]),
                 "posgram":jada[kolmik[0]:kolmik[1]],
                 "start_token":kolmik[0],
                 "end_token":kolmik[1]-1,
                 "trigram":kolmik[3],
                 "type":"post" if kolmik[4]=="taga" else "pre",
                 "context":kolmik[5],
                 "percent":kolmik[6]
              }
              kandidaadid.append(kandidaat)
           vastus.append({
             "sentence": lause.text,
             "sentence_posgram": "^"+jada,
             "error_candidates": kandidaadid
           })           
        return vastus


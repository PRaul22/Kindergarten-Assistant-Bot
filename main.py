from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os
import json
import requests
from dotenv import load_dotenv
from SPARQLWrapper import SPARQLWrapper, JSON
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def interogheaza_rdf4j(nume_gradinita: str):
    sparql = SPARQLWrapper("http://localhost:8080/rdf4j-server/repositories/grafexamen")
    
    interogare = f"""
    PREFIX : <http://exemplu.ro/proiectR&S#>
    SELECT ?numeCurs ?pret
    WHERE {{
        ?gradinita :nume "{nume_gradinita}" .
        ?gradinita :oferaCurs ?curs .
        ?curs :numeCurs ?numeCurs .
        ?curs :pret ?pret .
    }}
    """
    
    sparql.setQuery(interogare)
    sparql.setReturnFormat(JSON)
    
    try:
        rezultat = sparql.query().convert()
        cursuri = []
        for rand in rezultat["results"]["bindings"]:
            cursuri.append({
                "nume_curs": rand["numeCurs"]["value"],
                "pret_ron": rand["pret"]["value"]
            })
        return json.dumps(cursuri)
    except Exception:
        return json.dumps([])
    
def cauta_gradinita_dupa_cartier(cartier: str):
    url = f"http://localhost:4000/gradinite?cartier={cartier}"
    raspuns = requests.get(url)
    
    if raspuns.status_code == 200:
        date = raspuns.json()
        return json.dumps(date)
    
    return json.dumps([])

def extrage_cursuri_graphql(nume_gradinita: str):
    url = "http://localhost:3000/graphql"
    interogare = """
    query {
        allGradinites(filter: {nume: "%s"}) { id }
        allCursuris { gradinitaId nume_curs pret_ron }
    }
    """ % nume_gradinita
    
    try:
        date = requests.post(url, json={"query": interogare}).json()["data"]
        id_grad = str(date["allGradinites"][0]["id"])
        cursuri_filtrate = [c for c in date["allCursuris"] if str(c.get("gradinitaId")) == id_grad]
        
        return json.dumps({"gradinita": nume_gradinita, "cursuri": cursuri_filtrate})
    except Exception:
        return json.dumps([])
    
def adauga_curs_json(gradinita_id: int, nume_curs: str, pret_ron: int):
    url = "http://localhost:4000/cursuri"
    date_noi = {
        "gradinitaId": gradinita_id,
        "nume_curs": nume_curs,
        "pret_ron": pret_ron,
        "frecventa_saptamanala": 1
    }
    raspuns = requests.post(url, json=date_noi)
    
    if raspuns.status_code in [200, 201]:
        return json.dumps({"status": "succes", "mesaj": f"Cursul {nume_curs} a fost adăugat."})
    
    return json.dumps({"status": "eroare", "mesaj": "Nu s-a putut adăuga cursul."})

def adauga_curs_graphql(gradinita_id: int, nume_curs: str, pret_ron: int):
    url = "http://localhost:3000/graphql"
    interogare = """
    mutation {
        createCursuri(gradinitaId: %d, nume_curs: "%s", pret_ron: %d, frecventa_saptamanala: 1) {
            id
        }
    }
    """ % (gradinita_id, nume_curs, pret_ron)
    
    raspuns = requests.post(url, json={"query": interogare})
    if raspuns.status_code == 200:
        return json.dumps({"status": "succes", "mesaj": "Adăugat prin GraphQL."})
    return json.dumps({"status": "eroare"})

def adauga_curs_rdf4j(nume_curs: str, pret_ron: int):
    sparql = SPARQLWrapper("http://localhost:8080/rdf4j-server/repositories/grafexamen/statements")
    sparql.setMethod('POST')
    
    id_nod = nume_curs.replace(" ", "")
    
    interogare = f"""
    PREFIX : <http://exemplu.ro/proiectR&S#>
    INSERT DATA {{
        :Curs_{id_nod} a :CursOptional ;
                       :numeCurs "{nume_curs}" ;
                       :pret {pret_ron} .
    }}
    """
    sparql.setQuery(interogare)
    try:
        sparql.query()
        return json.dumps({"status": "succes", "mesaj": "Curs adăugat în RDF4J."})
    except Exception:
        return json.dumps({"status": "eroare"})
    
lista_unelte = [
    {
        "type": "function",
        "function": {
            "name": "cauta_gradinita_dupa_cartier",
            "description": "Cauta gradinite private in orasul Sibiu pe baza cartierului.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cartier": {"type": "string", "description": "Numele cartierului din Sibiu"}
                },
                "required": ["cartier"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extrage_cursuri_graphql",
            "description": "Extrage lista de cursuri optionale si preturile pentru o anumita gradinita folosind GraphQL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nume_gradinita": {"type": "string", "description": "Numele gradinitei"}
                },
                "required": ["nume_gradinita"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "interogheaza_rdf4j",
            "description": "Extrage cursurile si preturile din baza de cunostinte semantica RDF4J pentru o gradinita.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nume_gradinita": {"type": "string", "description": "Numele gradinitei cautate"}
                },
                "required": ["nume_gradinita"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "adauga_curs_json",
            "description": "Adauga un curs optional nou pentru o gradinita in baza de date principala (JSON Server).",
            "parameters": {
                "type": "object",
                "properties": {
                    "gradinita_id": {"type": "integer", "description": "ID-ul gradinitei"},
                    "nume_curs": {"type": "string", "description": "Numele cursului nou"},
                    "pret_ron": {"type": "integer", "description": "Pretul cursului in RON"}
                },
                "required": ["gradinita_id", "nume_curs", "pret_ron"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "adauga_curs_graphql",
            "description": "Adauga un curs optional nou pentru o gradinita folosind serverul GraphQL (Mutation).",
            "parameters": {
                "type": "object",
                "properties": {
                    "gradinita_id": {"type": "integer", "description": "ID-ul gradinitei"},
                    "nume_curs": {"type": "string", "description": "Numele cursului nou"},
                    "pret_ron": {"type": "integer", "description": "Pretul cursului in RON"}
                },
                "required": ["gradinita_id", "nume_curs", "pret_ron"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "adauga_curs_rdf4j",
            "description": "Adauga un curs optional nou in baza de date semantica (RDF4J).",
            "parameters": {
                "type": "object",
                "properties": {
                    "nume_curs": {"type": "string", "description": "Numele cursului nou"},
                    "pret_ron": {"type": "integer", "description": "Pretul cursului in RON"}
                },
                "required": ["nume_curs", "pret_ron"]
            }
        }
    }
]

harta_functii = {
    "cauta_gradinita_dupa_cartier": cauta_gradinita_dupa_cartier,
    "extrage_cursuri_graphql": extrage_cursuri_graphql,
    "interogheaza_rdf4j": interogheaza_rdf4j,
    "adauga_curs_json": adauga_curs_json,
    "adauga_curs_graphql": adauga_curs_graphql,
    "adauga_curs_rdf4j": adauga_curs_rdf4j
}

class UserRequest(BaseModel):
    mesaj: str

@app.post("/chat")
def chat_cu_asistentul(request: UserRequest):
    mesaje_conversatie = [
        {"role": "system", "content": "Esti un asistent util care ajuta parintii sa gaseasca gradinite si cursuri in Sibiu."},
        {"role": "user", "content": request.mesaj}
    ]

    raspuns_initial = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=mesaje_conversatie,
        tools=lista_unelte,
        tool_choice="auto"
    )

    mesaj_ai = raspuns_initial.choices[0].message
    mesaje_conversatie.append(mesaj_ai)

    if mesaj_ai.tool_calls:
        for tool_call in mesaj_ai.tool_calls:
            nume_functie = tool_call.function.name
            argumente = json.loads(tool_call.function.arguments)
            
            functie_reala = harta_functii.get(nume_functie)
            if functie_reala:
                rezultat_db = functie_reala(**argumente)
                
                mesaje_conversatie.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": nume_functie,
                    "content": rezultat_db
                })

        raspuns_final = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=mesaje_conversatie
        )
        return {"raspuns": raspuns_final.choices[0].message.content}

    return {"raspuns": mesaj_ai.content}
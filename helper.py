from PIL import Image
import requests, functools, time, pdb, json, os, random, torch, transformers
from io import BytesIO, StringIO
import numpy as np
import pandas as pd

def save_json(data, path):
    folder = os.path.dirname(path)
    os.makedirs(folder, exist_ok=True)

    with open(path, 'w') as f:
        json.dump(data, f, indent=4)
        
def read_json(path):
    with open(path) as f:
        data = json.load(f)
    return data

def read_jsonl(file_path):
    # Read jsonl file line by line
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():  # Skip empty lines
                # Wrap the JSON string in StringIO to resolve deprecation warning
                data.append(pd.read_json(StringIO(line), typ='series'))
    return pd.DataFrame(data)


def retry_if_fail(func):
    @functools.wraps(func)
    def wrapper_retry(*args, **kwargs):
        retry = 0
        while retry <= 2:
            try:
                out = func(*args, **kwargs)
                break
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except pdb.bdb.BdbQuit:
                raise pdb.bdb.BdbQuit
            except Exception as e:
                retry += 1
                time.sleep(10)
                print(f"Exception occurred: {type(e).__name__}, {e.args}")
                print(f"Retry {retry} times...")

        if retry > 10:
            out = {'output': 'ERROR'}
            print('ERROR')
        
        return out
    return wrapper_retry

def get_image(image_path: str):
    if image_path.startswith('http://') or image_path.startswith('https://'):
        response = requests.get(image_path)
        image = Image.open(BytesIO(response.content)).convert("RGB")
    else:
        image = Image.open(image_path).convert("RGB")
    return image

def get_image_size(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
    return width*height

def display_image(image_path: str):
    image = get_image(image_path)
    display(image)

def print_configs(args):
    # print experiment configuration
    args_dict = vars(args)
    print("########"*3)
    print('## Experiment Setting:')
    print("########"*3)
    for key, value in args_dict.items():
        print(f"| {key}: {value}")
    print("########"*3)
    
def set_seed(seed):
    np.random.seed(seed)
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.enabled = False
    transformers.set_seed(seed)

def score_meme(
    meme_path,
    call_model,
    max_intermediate_tokens=300,
    max_new_tokens=1,
):
    # # Cognitive Processing & Comprehension
    # cpc1 = "Is there a clear incongruity or surprise element?"
    # cpc2 = "Does it require/enable a reinterpretation?"
    # cpc3 = "Is it moderately difficult to understand (not too simple or too complex)?"

    # # Violation & Benign Nature
    # vbn1 = "Does it contain a violation (something wrong/unexpected/norm-breaking)?"
    # vbn2 = "Is this violation also perceived as harmless or non-threatening?"
    # vbn3 = "Does it maintain the 'sweet spot' between being threatening and benign?"

    # # Diminishment & Reframing
    # dr1 = "Does it make something seemingly important appear more trivial?"
    # dr2 = "Does it create a humorous reframing of the initial interpretation?"
    # dr3 = "Does it transform serious content into something playful?"

    # # Elaboration Potential
    # ep1 = "Can it generate multiple humor-relevant thoughts/interpretations?"
    # ep2 = "Does it connect to broader contexts or references?"
    # ep3 = "Can people build additional humor from the initial joke?"

    # # Integration of Elements
    # ie1 = "How well do visual and textual elements work together?"
    # ie2 = "Do multiple elements create additional layers of meaning?"
    # ie3 = "Does the combination enhance the humor?"

    # # (Ignore) Context & Relevance
    # cr1 = "Is it appropriate for its intended audience?"
    # cr2 = "Does it rely on shared cultural/social knowledge?"
    # cr3 = "Is it timely and relevant to current contexts?"

    def process_score(o, q):
        try:
            return max(min(int(o), q['score_range'][1]), q['score_range'][0])
        except ValueError:
            return None
    
    def get_score(q):
        output_1 = call_model(
            q['question'],
            [meme_path],
            max_new_tokens=max_intermediate_tokens,
            save_history=True,
        )

        output_2 = call_model(
            q['rating'],
            [],
            max_new_tokens = max_new_tokens,
            history = output_1['history'],
            save_history = True
        )

        output_dict = {
            'score': process_score(output_2['output'], q),
            'analysis': output_1['output'] + output_2['output'],
        }

        return output_dict


    humor_questions = {}
    output_control = " Make sure your response is a number without any other words."

    #############################
    ### Primary Factors (45%) ###
    #############################

    ### * Cognitive Processing (20%) ###

    humor_questions['cp1'] = {
        "question": "Is there a clear contrast between initial and final interpretations?",
        "score_range": 7,
    }
    humor_questions['cp1']['rating'] = f"Please give a score between 0 and {humor_questions['cp1']['score_range']}, where 0 means no contrast and {humor_questions['cp1']['score_range']} means very clear contrast."

    humor_questions['cp2'] = {
        "question": "Does the viewer arrive at a satisfying new understanding?",
        "score_range": 7,
    }
    humor_questions['cp2']['rating'] = f"Please assign a score between 0 and {humor_questions['cp2']['score_range']}, where 0 means no new understanding and {humor_questions['cp2']['score_range']} means highly satisfying realization."

    humor_questions['cp3'] = {
        "question": "Is the meme at an appropriate difficulty level - neither too obvious nor too complex?",
        "score_range": 6,
    }
    humor_questions['cp3']['rating'] = f"Please provide a score between 0 and {humor_questions['cp3']['score_range']}, where 0 means inappropriate difficulty and {humor_questions['cp3']['score_range']} means perfect difficulty level."

    ### * Violation & Benign Nature (25%) ###

    humor_questions['vbn1'] = {
        "question": "Does this meme contains something wrong/unexpected/norm-breaking?",
        "score_range": 8,
        "example": "To give you an example, the the meme with text 'Boss: why arent you working?\n Me: I didnt see you coming' has score 7.",
    }
    humor_questions['vbn1']['rating'] = f"Please give a score between 0 and {humor_questions['vbn1']['score_range']}, where 0 means no violation and {humor_questions['vbn1']['score_range']} means a clear and strong violation."

    humor_questions['vbn2'] = {
        "question": "To what extent can the violation be interpreted as playful or non-threatening?",
        "score_range": 8,
    }
    humor_questions['vbn2']['rating'] = f"Please assign a score between 0 and {humor_questions['vbn2']['score_range']}, where 0 means threatening/offensive and {humor_questions['vbn2']['score_range']} means completely harmless."

    humor_questions['vbn3'] = {
        "question": "How well does this meme balance being provocative yet acceptable?",
        "score_range": 9,
    }
    humor_questions['vbn3']['rating'] = f"Please provide a score between 0 and {humor_questions['vbn3']['score_range']}, where 0 means poorly balanced and {humor_questions['vbn3']['score_range']} means perfectly balanced."

    ###############################
    ### Secondary Factors (40%) ###
    ###############################

    ### * Diminishment & Reframing (25%) ###

    humor_questions['dr1'] = {
        "question": "How effectively does this meme reduce the importance/seriousness of its subject?",
        "score_range": 12,
    }
    humor_questions['dr1']['rating'] = f"Please give a score between 0 and {humor_questions['dr1']['score_range']}, where 0 means no reduction and {humor_questions['dr1']['score_range']} means highly effective diminishment."

    humor_questions['dr2'] = {
        "question": "How successfully does this meme transform something serious into something humorous?",
        "score_range": 13,
    }
    humor_questions['dr2']['rating'] = f"Please assign a score between 0 and {humor_questions['dr2']['score_range']}, where 0 means no transformation and {humor_questions['dr2']['score_range']} means perfect transformation."

    ### * Elaboration Potential (15%) ###

    humor_questions['ep1'] = {
        "question": "Can this meme be interpreted in multiple valid ways?",
        "score_range": 5,
    }
    humor_questions['ep1']['rating'] = f"Please provide a score between 0 and {humor_questions['ep1']['score_range']}, where 0 means single interpretation and {humor_questions['ep1']['score_range']} means multiple rich interpretations."
    
    humor_questions['ep2'] = {
        "question": "How well does this meme connect to other memes, cultural references, or shared experiences?",
        "score_range": 5,
    }
    humor_questions['ep2']['rating'] = f"Please provide a score between 0 and {humor_questions['ep2']['score_range']}, where 0 means no connections and {humor_questions['ep2']['score_range']} means rich connections."
    
    humor_questions['ep3'] = {
        "question": "What is the potential for creative variations or responses to this meme?",
        "score_range": 5,
    }
    humor_questions['ep3']['rating'] = f"Please provide a score between 0 and {humor_questions['ep3']['score_range']}, where 0 means no potential and {humor_questions['ep3']['score_range']} means high potential."

    ###############################
    ### Supporting Factor (15%) ###
    ###############################

    ### * Integration of Elements (15%) ###

    humor_questions['ie1'] = {
        "question": "How well do the visual and textual elements work together in this meme?",
        "score_range": 7,
    }
    humor_questions['ie1']['rating'] = f"Please provide a score between 0 and {humor_questions['ie1']['score_range']}, where 0 means poor integration and {humor_questions['ie1']['score_range']} means perfect integration."

    humor_questions['ie2'] = {
        "question": "Does the combination of elements create meaning beyond their individual parts?",
        "score_range": 8,
    }
    humor_questions['ie2']['rating'] = f"Please provide a score between 0 and {humor_questions['ie2']['score_range']}, where 0 means no enhanced meaning and {humor_questions['ie2']['score_range']} means significant enhanced meaning."
    scores, outputs = {}, {}
    for q in ["cp1", "cp2", "cp3"]:
        outputs[q] = get_score(humor_questions[q])
        scores[q] = process_score(outputs[q]['score'], humor_questions[q])

        if scores[q] is None: 
            return {
                'score': -1,
                'scores': scores,
                'outputs': outputs,
            }

    score_cp = sum([scores['cp1'], scores['cp2'], scores['cp3']])
    if score_cp < 12: 
        return {
            'score': score_cp,
            'scores': scores,
            'outputs': outputs,
        }


    for q in ["vbn1", "vbn2", "vbn3", "dr1", "dr2", "ep1", "ep2", "ep3", "ie1", "ie2"]:
        outputs[q] = get_score(humor_questions[q])
        scores[q] = process_score(outputs[q]['score'], humor_questions[q])

        if scores[q] is None: scores[q] = 0

    return {
        'score': sum(scores.values()),
        'scores': scores,
        'outputs': outputs,
    }
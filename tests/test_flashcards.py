import pytest
import requests
from tests.utils.test_db import client, test_db

# URLs
flashcard_generation_url = "v1/flashcards/generate"
fetch_flashcard_sets_url = "/v1/flashcards"
fetch_flashcards_url = "/v1/flashcards/set"
register_url = "/v1/auth/register"
login_url = "/v1/auth/login"
test_server = "http://staging.api.vlecture.tech"

# Variables
AUTH_HEADER = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmaXJzdF9uYW1lIjoibWFuZGEiLCJlbWFpbCI6Im1hbmRhdGVzQGdtYWlsLmNvbSIsImV4cCI6MTcxMTI0ODgxOX0.qrMHZkrM6wEFK_0LzkXqchCk1Dv6gSkt3qtnVIdDuvo"
}
VALID_USER_ID = "5acb2e38-0636-4b71-a468-fd695b5d4a27"
VALID_USER_ID_NO_SET = "5acb2e38-0636-4b71-a468-fd695b5d4a00"
VALID_NOTE_ID = "6607f18a8442899bdf95b03f"
VALID_SET_ID = "5acb2e38-0636-4b71-a468-fd695b5d4a25"
VALID_MAIN = "This week the UK Human Fertilisation and Embryology Authority okayed a proposal to modify human embryos through gene editing. The research, which will be carried out at the Francis Crick Institute in London, should improve our understanding of human development. It will also undoubtedly attract controversy - particularly with claims that manipulating embryonic genomes is a first step towards designer babies. Those concerns shouldn't be ignored. After all, gene editing of the kind that will soon be undertaken at the Francis Crick Institute doesn't occur naturally in humans or other animals. It is, however, a lot more common in nature than you might think, and it's been going on for a surprisingly long time - revelations that have challenged what biologists thought they knew about the way evolution works. We're talking here about one particular gene editing technique called CRISPR-Cas, or just CRISPR. It's relatively fast, cheap and easy to edit genes with CRISPR - factors that explain why the technique has exploded in popularity in the last few years. But CRISPR wasn't dreamed up from scratch in a laboratory. This gene editing tool actually evolved in single-celled microbes. CRISPR went unnoticed by biologists for decades. It was only at the tail end of the 1980s that researchers studying Escherichia coli noticed that there were some odd repetitive sequences at the end of one of the bacterial genes. Later, these sequences would be named Clustered Regularly Interspaced Short Palindromic Repeats - CRISPRs. For several years the significance of these CRISPRs was a mystery, even when researchers noticed that they were always separated from one another by equally odd 'spacer' gene sequences. Then, a little over a decade ago, scientists made an important discovery. Those 'spacer' sequences look odd because they aren't bacterial in origin. Many are actually snippets of DNA from viruses that are known to attack bacteria. In 2005, three research groups independently reached the same conclusion: CRISPR and its associated genetic sequences were acting as a bacterial immune system. In simple terms, this is how it works. A bacterial cell generates special proteins from genes associated with the CRISPR repeats (these are called CRISPR associated - Cas - proteins). If a virus invades the cell, these Cas proteins bind to the viral DNA and help cut out a chunk. Then, that chunk of viral DNA gets carried back to the bacterial cell's genome where it is inserted - becoming a spacer. From now on, the bacterial cell can use the spacer to recognise that particular virus and attack it more effectively. These findings were a revelation. Geneticists quickly realised that the CRISPR system effectively involves microbes deliberately editing their own genomes - suggesting the system could form the basis of a brand new type of genetic engineering technology. They worked out the mechanics of the CRISPR system and got it working in their lab experiments. It was a breakthrough that paved the way for this week's announcement by the HFEA. Exactly who took the key steps to turn CRISPR into a useful genetic tool is, however, the subject of a huge controversy. Perhaps that's inevitable - credit for developing CRISPR gene editing will probably guarantee both scientific fame and financial wealth. Beyond these very important practical applications, though, there's another CRISPR story. It's the account of how the discovery of CRISPR has influenced evolutionary biology. Sometimes overlooked is the fact that it wasn't just geneticists who were excited by CRISPR's discovery - so too were biologists. They realised CRISPR was evidence of a completely unexpected parallel between the way humans and bacteria fight infections. We've known for a long time that part of our immune system \"learns\" about the pathogens it has seen before so it can adapt and fight infections better in future. Vertebrate animals were thought to be the only organisms with such a sophisticated adaptive immune system. In light of the discovery of CRISPR, it seemed some bacteria had their own version. In fact, it turned out that lots of bacteria have their own version. At the last count, the CRISPR adaptive immune system was estimated to be present in about 40% of bacteria. Among the other major group of single-celled microbes - the archaea - CRISPR is even more common. It's seen in about 90% of them. If it's that common today, CRISPR must have a history stretching back over millions - possibly even billions - of years. \"It's clearly been around for a while,\" says Darren Griffin at the University of Kent. The animal adaptive immune system, then, isn't nearly as unique as we thought. And there's one feature of CRISPR that makes it arguably even better than our adaptive immune system: CRISPR is heritable. When we are infected by a pathogen, our adaptive immune system learns from the experience, making our next encounter with that pathogen less of an ordeal. This is why vaccination is so effective: it involves priming us with a weakened version of a pathogen to train our adaptive immune system. Your children, though, won't benefit from the wealth of experience locked away in your adaptive immune system. They have to experience an infection - or be vaccinated - first hand before they can learn to deal with a given pathogen. CRISPR is different. When a microbe with CRISPR is attacked by a virus, the record of the encounter is hardwired into the microbe's DNA as a new spacer. This is then automatically passed on when the cell divides into daughter cells, which means those daughter cells know how to fight the virus even before they've seen it. We don't know for sure why the CRISPR adaptive immune system works in a way that seems, at least superficially, superior to ours. But perhaps our biological complexity is the problem, says Griffin. \"In complex organisms any minor [genetic] changes cause profound effects on the organism,\" he says. Microbes might be sturdy enough to constantly edit their genomes during their lives and cope with the consequences - but animals probably aren't. The discovery of this heritable immune system was, however, a biologically astonishing one. It means that some microbes write their lifetime experiences of their environment into their genome and then pass the information to their offspring – and that is something that evolutionary biologists did not think happened. Darwin's theory of evolution is based on the idea that natural selection acts on the naturally occurring random variation in a population. Some organisms are better adapted to the environment than others, and more likely to survive and reproduce, but this is largely because they just happened to be born that way. But before Darwin, other scientists had suggested different mechanisms through which evolution might work. One of the most famous ideas was proposed by a French scientist called Jean-Bapteste Lamarck. He thought organisms actually changed during their life, acquiring useful new adaptations non-randomly in response to their environmental experiences. They then passed on these changes to their offspring. People often use giraffes to illustrate Lamarck's hypothesis. The idea is that even deep in prehistory, the giraffe's ancestor had a penchant for leaves at the top of trees. This early giraffe had a relatively short neck, but during its life it spent so much time stretching to reach leaves that its neck lengthened slightly. The crucial point, said Lamarck, was that this slightly longer neck was somehow inherited by the giraffe's offspring. These giraffes also stretched to reach high leaves during their lives, meaning their necks lengthened just a little bit more, and so on. Once Darwin's ideas gained traction, Lamarck's ideas became deeply unpopular. But the CRISPR immune system - in which specific lifetime experiences of the environment are passed on to the next generation - is one of a tiny handful of natural phenomena that arguably obeys Lamarckian principles. \"The realisation that Lamarckian type of evolution does occur and is common enough, was as startling to biologists as it seems to a layperson,\" says Eugene Koonin at the National Institutes of Health in Bethesda, Maryland, who explored the idea with his colleagues in 2009, and does so again in a paper due to be published later this year. This isn't to say that all of Lamarck's thoughts on evolution are back in vogue. \"Lamarck had additional ideas that were important to him, such as the inherent drive to perfection that to him was a key feature of evolution,\" says Koonin. No modern evolutionary biologist goes along with that idea. But the discovery of the CRISPR system still implies that evolution isn't purely the result of Darwinian random natural selection. It can sometimes involve elements of non-random Lamarckism too – a \"continuum\", as Koonin puts it. In other words, the CRISPR story has had a profound scientific impact far beyond the doors of the genetic engineering lab. It truly was a transformative discovery."
VALID_MAIN_WORD_COUNT = 248
LANGUAGE = "English"
VALID_NUM_OF_FLASHCARDS = 3

INVALID_NOTE_ID = 2
INVALID_MAIN_1 = ""
INVALID_MAIN_2 = "0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789"
INVALID_MAIN_3 = "!@#$%^&*()_+-=[]{}|;':,./<>?!@#$%^&*()_+-=[]{}|;':,./<>?!@#$%^&*()_+-=[]{}|;':,./<>?!@#$%^&*()_+-[]{}|;':,./<>?!@#$%^&*()_+-=[]{}|;':"
INVALID_MAIN_WORD_COUNT_1 = 0
INVALID_NUM_OF_FLASHCARDS_1 = 0
INVALID_MAIN_WORD_COUNT_1 = -1
INVALID_NUM_OF_FLASHCARDS_1 = -1
INVALID_MAIN_WORD_COUNT_1 = 11
INVALID_NUM_OF_FLASHCARDS_1 = 11

EDGE_MAIN = "0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789 7890123456789012345678901 7890123456789012345678901 7890123456789012345678901 7890123456789012345678901 7890123456789012345678901 7890123456789012345678901 7890123456789012345678901 7890123456789012345678901 7890123456789012345678901 7890123456789012345678901 7890123456789012345678901 7890123456789012345678901 7890123456789012345678901  This week the UK Human Fertilisation and Embryology Authority okayed a proposal to modify human embryos through gene editing. The research, which will be carried out at the Francis Crick Institute in London, should improve our understanding of human development. It will also undoubtedly attract controversy - particularly with claims that manipulating embryonic genomes is a first step towards designer babies. 0123456789 01234567890123456 7890123456789012345678901 789012345678901234567890178901234567890123456789017890123456789012345678901789012345678901234567890178901234567890123456789012 3456789012 34567890123456789 34567890123456789 34567890123456789 34567890123456789 34567890123456789 34567890123456789 34567890123456789 34567890123456789 34567890123456789 34567890123456789 34567890123456789 34567890123456789 34567890123456789 0123456789 7890123456789012345678901"

# Generate Flashcards Test Cases
## Positive Cases
def test_generate_flashcards_positive(test_db): # Valid input
    access_token = login()
    header = set_header(access_token)
    response = client.post(
        flashcard_generation_url,
        json={
            "note_id": VALID_NOTE_ID,
            "main": VALID_MAIN,
            "main_word_count": VALID_MAIN_WORD_COUNT,
            "language": LANGUAGE,
            "num_of_flashcards": VALID_NUM_OF_FLASHCARDS,
        },
        headers=header
    )

    assert response.status_code == 200

## Negative Cases
def test_generate_flashcards_negative(test_db): # Invalid input - empty field
    access_token = login()
    header = set_header(access_token)
    response = client.post(
        flashcard_generation_url,
        json={
            "note_id": "",
            "main": "",
            "main_word_count": "",
            "language": "",
            "num_of_flashcards": 0,
        },
        headers=header
    )

    assert response.status_code == 422

## Edge Cases
def test_generate_flashcards_edge(test_db): # Edge case input - 60 Valid words, 40 Numeric words, 2 Flashcards
    access_token = login()
    header = set_header(access_token)
    response = client.post(
        flashcard_generation_url,
        json={
            "note_id": VALID_NOTE_ID,
            "main": EDGE_MAIN,
            "main_word_count": VALID_MAIN_WORD_COUNT,
            "language": LANGUAGE,
            "num_of_flashcards": 2,
        },
        headers=header
    )

    assert response.status_code == 200

# Positive Cases
def test_fetch_flashcard_sets_positive(test_db):
    response = requests.get(
        test_server + fetch_flashcard_sets_url, 
        headers=AUTH_HEADER,
        json={"user_id" : VALID_USER_ID}
    )

    assert response.status_code == 200
    assert response.json()['message'] == "Succesfully fetched all flashcard sets from current user."

def test_fetch_flashcards_positive(test_db):
    response = requests.get(
        test_server + fetch_flashcards_url, 
        headers=AUTH_HEADER,
        json={"note_id" : VALID_NOTE_ID, "set_id": VALID_SET_ID}
    )
   
    assert response.status_code == 200
    assert response.json()['message'] == "Succesfully fetched all flashcards from set."
    
# Negative Cases
def test_fetch_flashcard_sets_not_logged_in(test_db):
    response = requests.get(
        test_server + fetch_flashcard_sets_url, 
        json={"user_id" : VALID_USER_ID}
    )

    assert response.status_code == 401 
    assert response.json()['error'] == "You don't have access to these flashcard sets or flashcard sets don't exist."

def test_fetch_flashcards_not_logged_in(test_db):
    response = requests.get(
        test_server + fetch_flashcards_url, 
        json={"note_id" : VALID_NOTE_ID, "set_id": VALID_SET_ID}
    )

    assert response.status_code == 401
    assert response.json()['error'] == "You don't have access to these flashcards or flashcards don't exist."

# Edge Cases
def test_fetch_flashcard_sets_no_sets(test_db):
    response = requests.get(
        test_server + fetch_flashcard_sets_url, 
        headers=AUTH_HEADER,
        json={"user_id" : VALID_USER_ID_NO_SET}
    )

    assert response.status_code == 200
    assert response.json()['message'] == "Succesfully fetched all flashcard sets from current user."

# Helper Functions
def login():
    client.post(
        register_url,
        json={
            "email": "positive@example.com",
            "first_name": "Positive",
            "middle_name": "Test",
            "last_name": "Case",
            "password": "positivepassword",
        },
    )
    response = client.post(
        login_url,
        json={"email": "positive@example.com", "password": "positivepassword"},
    )

    return response.json()["access_token"]

def set_header(token):
    headers = {"Authorization": f"Bearer {token}"}
    return headers
NOTE_ID = "66214575dee0152b709ba24d"

INVALID_NOTE_ID = "abcdefghijklmnopqrstuvwx"

NOTE_MAIN_DATA_ARRAY = [
  "The UK Human Fertilisation and Embryology Authority approved a proposal for gene editing on human embryos at the Francis Crick Institute in London.",
  "Gene editing using CRISPR-Cas is a fast, cheap, and effective technique that has exploded in popularity in recent years.",
  "CRISPR, initially unnoticed by biologists, was discovered to be a bacterial immune system that involves Cas proteins cutting out viral DNA and inserting it into the bacterial cell's genome as a spacer.",
  "CRISPR is heritable, passing on the learned response to viruses to daughter cells, unlike the human adaptive immune system which requires individual experience for learning.",
  "The discovery of CRISPR challenges traditional views on evolution, suggesting a Lamarckian mechanism where experiences are passed on to offspring.",
]

NOTE_CUES_DATA_ARRAY = [
  "UK Human Fertilisation and Embryology Authority",
  "Francis Crick Institute in London",
  "CRISPR-Cas gene editing",
  "Bacterial immune system - Cas proteins, viral DNA cutting, spacer insertion",
  "Heritability of CRISPR response",
  "Challenges to traditional evolution theories - Lamarckism",
]

NOTE_SUMMARY_DATA_ARRAY = [
  "The lecture discusses the approval of gene editing on human embryos by the UK Human Fertilisation and Embryology Authority at the Francis Crick Institute in London. The use of CRISPR-Cas, a popular gene editing technique, was explained, highlighting its bacterial immune system mechanism involving Cas proteins. Unlike the human adaptive immune system, CRISPR provides a heritable response to viruses. This discovery challenges traditional views on evolution, suggesting a Lamarckian mechanism where learned responses are passed on to offspring.",
]

NOTE_MAIN_DATA = "\n".join(NOTE_MAIN_DATA_ARRAY)
NOTE_CUES_DATA = "\n".join(NOTE_CUES_DATA_ARRAY)
NOTE_SUMMARY_DATA = "\n".join(NOTE_SUMMARY_DATA_ARRAY)

NOTE_TEXT_SPLITTING_INPUT = f"This is a Cornell-notetaking based Note. Note main content:\n{NOTE_MAIN_DATA}\n\nNote cues:\n{NOTE_CUES_DATA}\n\nNote summary: {NOTE_SUMMARY_DATA}"


EXPECTED_RESPONSE_NOTE_MONGODB = {
    "_id": "66214575dee0152b709ba24d",
    "owner_id": "043925c3-e18e-481a-a35e-2decc54b99bb",
    "title": "ujhugybjn",
    "subtitle": "",
    "created_at": "2024-04-18T16:08:21.167000",
    "updated_at": "2024-04-18T16:08:21.167000",
    "is_deleted": False,
    "is_edited": False,
    "is_published": False,
    "main": [
        {
            "id": "1c01038d-d542-42ec-8783-55d880be1b00",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "The company's main campaign for promotion this autumn will be the Pocket dictionary.",
                    "styles": {}
                }
            ],
            "children": []
        },
        {
            "id": "d6d1bf1f-5aff-4aeb-87a9-33b063313ba4",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "They also have a reasonable budget for the new roadmap coming out next month.",
                    "styles": {}
                }
            ],
            "children": []
        },
        {
            "id": "5d22f093-b9aa-4ac2-9054-1d602df0782c",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "Full-page adverts have been taken in travel magazines for both titles.",
                    "styles": {}
                }
            ],
            "children": []
        },
        {
            "id": "404248aa-8da6-44e3-a2f9-ab7d93b82573",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "Consideration is being given to including the dictionary in a new monthly reference.",
                    "styles": {}
                }
            ],
            "children": []
        },
        {
            "id": "75719931-c6fc-45bc-bef3-93ba6836051f",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "Designer has produced new stands for window and general shop displays.",
                    "styles": {}
                }
            ],
            "children": []
        },
        {
            "id": "d6db5d89-b04d-44e5-8751-70c1ab40236d",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "Range of free gifts like calendars, key rings, and possibly umbrellas for major clients are being considered for exhibitions.",
                    "styles": {}
                }
            ],
            "children": []
        },
        {
            "id": "c3b7e1f3-e38d-4c3b-9156-98e26d6032bf",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "Airtime on Radio East has been negotiated by Alison, and a visit to a TV network is planned for future titles.",
                    "styles": {}
                }
            ],
            "children": []
        },
        {
            "id": "18abd923-740b-4f08-9f5b-4a373d69f186",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "All publicity material is listed in the annual catalog to be sent to booksellers in December.",
                    "styles": {}
                }
            ],
            "children": []
        },
        {
            "id": "70b1c626-329a-4804-ae98-7219814d50bd",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "A bookseller mail shot will be sent out in September as an information sheet.",
                    "styles": {}
                }
            ],
            "children": []
        },
        {
            "id": "21407b3b-b06e-4356-a77e-d1b716f3999b",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "The venue for the dictionary launch party next month will be the management center with excellent catering.",
                    "styles": {}
                }
            ],
            "children": []
        }
    ],
    "cues": [
        {
            "id": "c38b520a-4ad2-4794-b1b0-6d1fa4b471e6",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "Main campaign: Pocket dictionary",
                    "styles": {}
                }
            ],
            "children": []
        },
        {
            "id": "0e7e7b9b-afe3-411f-a159-1e9ff0e2578e",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "Budget for new roadmap",
                    "styles": {}
                }
            ],
            "children": []
        },
        {
            "id": "a60e96fc-86fd-4109-9641-0b137afd16d1",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "Full-page adverts in travel magazines",
                    "styles": {}
                }
            ],
            "children": []
        },
        {
            "id": "17340326-41d6-48e2-a4e3-6c4ccbcc8f3e",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "Inclusion in new monthly reference",
                    "styles": {}
                }
            ],
            "children": []
        },
        {
            "id": "cbccb7fc-ad44-406b-8abd-f1d322dd56af",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "New designer stands",
                    "styles": {}
                }
            ],
            "children": []
        },
        {
            "id": "95965ad3-3900-44f6-99d8-122d8336a344",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "Free gifts for exhibitions",
                    "styles": {}
                }
            ],
            "children": []
        },
        {
            "id": "1e456a10-853a-4298-83eb-aa3dc243a433",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "Airtime on Radio East",
                    "styles": {}
                }
            ],
            "children": []
        },
        {
            "id": "1bdfcced-24eb-4fdc-b7df-c47025f182df",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "TV network visit",
                    "styles": {}
                }
            ],
            "children": []
        },
        {
            "id": "92a1991f-7c99-478f-a970-9483d8408277",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "Publicity material in annual catalog",
                    "styles": {}
                }
            ],
            "children": []
        },
        {
            "id": "eccf8fa5-bf9b-47bb-b693-296eacedb7a5",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "Bookseller mail shot in September",
                    "styles": {}
                }
            ],
            "children": []
        },
        {
            "id": "9e6da1f2-974b-4cf3-bea6-722917b03982",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "Launch party venue: management center",
                    "styles": {}
                }
            ],
            "children": []
        }
    ],
    "summary": [
        {
            "id": "e0686ca0-282f-4a31-ad76-3bf9b349f1d4",
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [
                {
                    "type": "text",
                    "text": "The company's marketing director outlined the main plans for promotion this autumn, focusing on the Pocket dictionary as the main campaign and allocating a budget for the new roadmap. Full-page adverts have been secured in travel magazines, with considerations for inclusion in a new monthly reference. New designer stands for displays have been produced, and a range of free gifts like calendars and key rings are being considered. Plans for airtime on Radio East and a visit to a TV network have been made. Publicity material will be listed in the annual catalog, with a bookseller mail shot scheduled for September. The venue for the dictionary launch party has been confirmed to be the management center with excellent catering.",
                    "styles": {}
                }
            ],
            "children": []
        }
    ],
    "language": "en-US",
    "main_word_count": 151
}
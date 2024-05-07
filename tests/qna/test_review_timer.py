import datetime

response_dummy_review = {
    "id": "662e2a6ba3710f88cd98aac3",
    "owner_id": "36d588f1-d595-4ae9-9ed9-a29ef2b16a05",
    "note_id": "6627ca99d71c70f23f210590",
    "created_at": "2024-04-30T14:13:00.124Z",
    "answers": [
        {
            "question_id": "270995cc-9d3e-4a6d-83ed-7693a90f75de",
            "answer_id": "d4311d9d-71f4-44a4-80e8-e50932470fde",
            "content": "Collaborating with a TV network",
            "created_at": "2024-04-30T14:13:28.144Z"
        },
        {
            "question_id": "11135862-8345-40e4-9725-0ebec2b4c86c",
            "answer_id": "7b77eacb-9218-4674-be39-93a41e66aa24",
            "content": "The company will sponsor a local sports team",
            "created_at": "2024-04-30T14:13:38.786Z"
        },
        {
            "question_id": "ba1d297a-82ae-4357-b278-10e780f6da39",
            "answer_id": "a9d4d44a-8153-4660-9396-f860e6e42f4a",
            "content": "Katering yang baik telah dipesan",
            "created_at": "2024-04-30T14:13:42.868Z"
        }
    ]
}

def calculate_total_elapsed_time(response_review):
    # Extract timestamps of the first and last questions
    created_payload = datetime.datetime.fromisoformat(response_review["created_at"].rstrip('Z'))
    last_created_at = datetime.datetime.fromisoformat(response_review["answers"][-1]["created_at"].rstrip('Z'))

    # Calculate the elapsed time in seconds
    elapsed_time = (last_created_at - created_payload).total_seconds()
    
    # Return the rounded down elapsed time
    return int(elapsed_time)

def calculate_question_elapsed_time(response_review, question_index):
    # Extract timestamps of the question and previous question or payload
    if question_index == 0:
        question_created_at = datetime.datetime.fromisoformat(response_review["answers"][0]["created_at"].rstrip('Z'))
        previous_timestamp = datetime.datetime.fromisoformat(response_review["created_at"].rstrip('Z'))
    else:
        question_created_at = datetime.datetime.fromisoformat(response_review["answers"][question_index]["created_at"].rstrip('Z'))
        previous_timestamp = datetime.datetime.fromisoformat(response_review["answers"][question_index - 1]["created_at"].rstrip('Z'))

    # Calculate the elapsed time in seconds
    elapsed_time = (question_created_at - previous_timestamp).total_seconds()
    
    # Return the rounded down elapsed time
    return int(elapsed_time)


def test_total_elapsed_time():
    # Expected total elapsed time is the difference between the last question and payload created_at times
    expected_total_elapsed_time = 42  # In seconds (2024-04-30T14:13:42.868 - 2024-04-30T14:13:00.124 = 32.744)

    # Calculate total elapsed time
    total_elapsed_time = calculate_total_elapsed_time(response_dummy_review)
    assert total_elapsed_time == expected_total_elapsed_time
    
    
def test_question_elapsed_time():
    # Expected individual question times
    expected_question_times = [28, 10, 4]  # In seconds

    # Calculate individual question times
    question_times = [calculate_question_elapsed_time(response_dummy_review, i) for i in range(len(response_dummy_review["answers"]))]
    assert question_times == expected_question_times
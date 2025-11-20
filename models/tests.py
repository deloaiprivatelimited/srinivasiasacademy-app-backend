from mongoengine import Document, StringField, DateTimeField, ListField, ReferenceField, IntField, EmbeddedDocument, EmbeddedDocumentField, DictField,FloatField
from datetime import timedelta
from models.student import Student
from models.question import Question  # Assuming you have a Question model


class QuestionDetail(EmbeddedDocument):
    id = StringField(required=True)  # Unique ID for the question
    question = StringField(required=True)  # The question text
    question_image = StringField(default=None)  # URL to an image, can be None or null
    option_a = DictField(required=True)  # Option A: {'text': '...', 'image_url': '...'}
    option_b = DictField(required=True)  # Option B: {'text': '...', 'image_url': '...'}
    option_c = DictField(required=True)  # Option C: {'text': '...', 'image_url': '...'}
    option_d = DictField(required=True)  # Option D: {'text': '...', 'image_url': '...'}
    correct_option = IntField(required=True, min_value=0, max_value=3)  # Correct option index (0 to 3)
    crt_ans_score = FloatField(default=3.0)  # Default value for correct answer score
    wrong_ans_score = FloatField(default=-0.25)  # Default value for wrong answer score
    def to_json(self):
        return {
            "id": str(self.id),
            "question": self.question,
            "question_image": self.question_image,
            "options": {
                "A": self.option_a,
                "B": self.option_b,
                "C": self.option_c,
                "D": self.option_d,
            },
            "correct_option": self.correct_option,
            "crt_ans_score": self.crt_ans_score,
            "wrong_ans_score": self.wrong_ans_score,
        }
class Response(EmbeddedDocument):
    question_id = StringField(required=True)  # ID of the question
    answer = StringField(required=True)  # Student's answer to the question

class Result(EmbeddedDocument):
    student_id = StringField(required=True)  # Student ID
    responses = ListField(EmbeddedDocumentField(Response))  # List of responses for each question
    score = FloatField(required=True)  # Student's score
    status=IntField(required=True,default=0)

class Test(Document):
    meta = {'collection': 'tests'}  # MongoDB collection name

    # Attributes
    name=StringField(required=True)
    start_date = DateTimeField(required=True)  # When the test starts
    start_time = StringField(required=True)  # Start time as a string (e.g., "10:00 AM")
    duration = IntField(required=True)  # Duration in minutes
    end_date = DateTimeField(required=True)  # When the test ends (can be calculated from start_date + duration)
    end_time = StringField(required=True)  # End time as a string (can be calculated)
    students_enrolled = ListField(ReferenceField('Student'))  # List of students enrolled in the test
    questions = ListField(EmbeddedDocumentField(QuestionDetail))  # List of questions for the test
    results = ListField(EmbeddedDocumentField(Result))  # List of results for each student
    order_index = IntField(default=0)


    def delete_test(self):
            # Remove the test from all enrolled students
            for student in self.students_enrolled:
                student.tests.remove(self)  # Remove the test reference
                student.save()  # Save changes to the student document

            # Now delete the test document
            self.delete()

            return True  # Indicate successful deletion
    # Methods
    @classmethod
    def remove_question(cls, test_id, question_id):
        test = cls.objects(id=test_id).first()
        
        if not test:
            raise ValueError("Test not found")

        # Find the question by its ID
        question_to_remove = next((q for q in test.questions if q.id == question_id), None)

        if question_to_remove:
            test.questions.remove(question_to_remove)  # Remove the question
            test.save()  # Save the changes
            return True
        else:
            raise ValueError("Question not found in the test")
    @classmethod
    def add_test(cls, start_date, start_time, duration, questions):
        test = cls(
            start_date=start_date,
            start_time=start_time,
            duration=duration,
            end_date=start_date + timedelta(minutes=duration),
            end_time=(start_date + timedelta(minutes=duration)).strftime("%I:%M %p"),
            questions=questions,
            results=[]  # Initialize results as an empty list
        )
        test.save()
        return test

    @classmethod
    def enroll_student(cls, test_id, student_id):
        test = cls.objects(id=test_id).first()
        student = Student.objects(id=student_id).first()
        
        if test and student:
            if student not in test.students_enrolled:
                test.students_enrolled.append(student)
                student.tests.append(test)
                student.save()
                test.save()
                return True
            else:
                return False  # Student is already enrolled
        else:
            raise ValueError("Test or Student not found")

    @classmethod
    def unenroll_student(cls, test_id, student_id):
        test = cls.objects(id=test_id).first()
        student = Student.objects(id=student_id).first()
        
        if test and student:
            if student in test.students_enrolled:
                test.students_enrolled.remove(student)
                test.results = [result for result in test.results if result.student_id != str(student_id)]

                student.tests.remove(test)  # Assuming the Student model has a 'tests' list
                student.save()
                test.save()
                return True
            else:
                return False  # Student is not enrolled in the test
        else:
            raise ValueError("Test or Student not found")
    @classmethod
    def record_result(cls, test_id, student_id, responses):
        test = cls.objects(id=test_id).first()
        
        if test:
            # Find existing result for the student
            existing_result = next((result for result in test.results if result.student_id == str(student_id)), None)

            # Calculate the score based on responses
            score = 0
            response_docs = []

            for response in responses:
                question_id = response['question_id']
                selected_answer = response['answer']
                
                # Find the corresponding question
                question = next((q for q in test.questions if q.id == question_id), None)
                if question:
                    correct_answer_index = question.correct_option

                    if selected_answer == "NA":
                        # Do nothing for NA
                        continue
                    elif selected_answer == ['A', 'B', 'C', 'D'][correct_answer_index]:
                        score += question.crt_ans_score  # Add points for correct answer
                    else:
                        score += question.wrong_ans_score  # Subtract points for wrong answer

                response_docs.append(Response(question_id=question_id, answer=selected_answer))

            if existing_result:
                # Update the existing result
                existing_result.responses = response_docs
                existing_result.score = score
                existing_result.status = 1  # Assuming status should be set to 1
            else:
                # Create a new Result document
                result = Result(student_id=str(student_id), responses=response_docs, score=score, status=1)
                test.results.append(result)

            test.save()  # Save the test with updated results
            return True
        else:
            raise ValueError("Test not found")

    # @classmethod
    # def record_result(cls, test_id, student_id, responses):
    #     test = cls.objects(id=test_id).first()
        
    #     if test:
    #         # Calculate the score based on responses
    #         score = 0
    #         response_docs = []

    #         for response in responses:
    #             question_id = response['question_id']
    #             selected_answer = response['answer']
    #             print(selected_answer)
                
    #             # Find the corresponding question
    #             question = next((q for q in test.questions if q.id == question_id), None)
    #             if question:
    #                 correct_answer_index = question.correct_option
    #                 print(question.question)

    #                 if selected_answer == "NA":
    #                     # Do nothing for NA
    #                     print("No answer provided (NA)")
    #                 elif selected_answer == ['A', 'B', 'C', 'D'][correct_answer_index]:
    #                     score += question.crt_ans_score  # Add points for correct answer
    #                     print("Correct answer selected")
    #                 else:
    #                     score += question.wrong_ans_score  # Subtract points for wrong answer
    #                     print("Wrong answer selected")

    #                 print(f"Current score: {score}")
                    
    #             response_docs.append(Response(question_id=question_id, answer=selected_answer))
            
    #         # Create a new Result document
    #         result = Result(student_id=str(student_id), responses=response_docs, score=score, status=1)
    #         test.results.append(result)  # Add result to the test
    #         test.save()
    #         return True
    #     else:
    #         raise ValueError("Test not found")
    def get_total_max_score(self):
        return sum(question.crt_ans_score for question in self.questions)

    def to_json_admin(self):
        json_data = {
            "id": str(self.id),
            "name" : self.name,
            "start_date": self.start_date,
            "start_time": self.start_time,
            "duration": self.duration,
            "end_date": self.end_date,
            "end_time": self.end_time,
            # "students_enrolled": [student.to_json() for student in self.students_enrolled],
            # "questions": [question.to_json() for question in self.questions],
            # "results": [
            #     {
            #         "student_id": result.student_id,
            #         "responses": [
            #             {
            #                 "question_id": response.question_id,
            #                 "answer": response.answer
            #             }
            #             for response in result.responses
            #         ],
            #         "score": result.score,
            #         "status":result.status
            #     }
            #     for result in self.results
            # ],  # Include results in the JSON output
        }
        return json_data

    def to_json(self):
        total_questions = len(self.questions)
        total_max_score = self.get_total_max_score()
        json_data = {
            "id": str(self.id),
            "name" : self.name,
            "start_date": self.start_date,
            "start_time": self.start_time,
            "duration": self.duration,
            "end_date": self.end_date,
            "end_time": self.end_time,
            "students_enrolled": [student.to_json() for student in self.students_enrolled],
            "questions": [question.to_json() for question in self.questions],
            "results": [
                {
                    "student_id": result.student_id,
                    "responses": [
                        {
                            "question_id": response.question_id,
                            "answer": response.answer
                        }
                        for response in result.responses
                    ],
                    "score": result.score,
                    "status":result.status
                }
                for result in self.results
            ],  # Include results in the JSON output
            "total_questions": total_questions,
            "total_max_score": total_max_score
        }
        return json_data


    def to_json_secure(self,student_id):
        total_questions = len(self.questions)
        total_max_score = self.get_total_max_score()
        json_data = {
        "id": str(self.id),
        "name": self.name,
        "start_date": self.start_date,
        "start_time": self.start_time,
        "duration": self.duration,
        "end_date": self.end_date,
        "end_time": self.end_time,
        "total_questions": total_questions,
            "total_max_score": total_max_score,
        "result": None  # Default to None
        }
        for result in self.results:
            if result.student_id == student_id:
                json_data["result"] = {
                    "student_id": result.student_id,
                    "responses": [
                        {
                            "question_id": response.question_id,
                            "answer": response.answer
                        }
                        for response in result.responses
                    ],
                    "score": result.score,
                                        "status":result.status

                }
                break  # Exit loop once the student result is found

        return json_data

    def to_json_secure_with_q(self,student_id):
        total_questions = len(self.questions)
        total_max_score = self.get_total_max_score()
       
        
        json_data = {
        "id": str(self.id),
        "name": self.name,
        "start_date": self.start_date,
        "start_time": self.start_time,
        "duration": self.duration,
        "end_date": self.end_date,
        "end_time": self.end_time,
        "total_questions": total_questions,
            "total_max_score": total_max_score,
                    "questions": [question.to_json() for question in self.questions],

        "result": None  # Default to None
        }
        for result in self.results:
            if result.student_id == student_id:
                json_data["result"] = {
                    "student_id": result.student_id,
                    "responses": [
                        {
                            "question_id": response.question_id,
                            "answer": response.answer
                        }
                        for response in result.responses
                    ],
                    "score": result.score,
                                        "status":result.status

                }
                break  # Exit loop once the student result is found

        return json_data

    def to_json_students(self):
        total_questions = len(self.questions)
        total_max_score = self.get_total_max_score()
        json_data = {
            "id": str(self.id),
            "name" : self.name,
            "start_date": self.start_date,
            "start_time": self.start_time,
            "duration": self.duration,
            "end_date": self.end_date,
            "end_time": self.end_time,
        "total_questions": total_questions,
            "total_max_score": total_max_score,
            "questions": [question.to_json() for question in self.questions],
            "results": [
                {
                    "student_id": result.student_id,
                    "responses": [
                        {
                            "question_id": response.question_id,
                            "answer": response.answer
                        }
                        for response in result.responses
                    ],
                    "score": result.score,

                                        "status":result.status

                }
                for result in self.results
            ]  # Include results in the JSON output
        }
        return json_data

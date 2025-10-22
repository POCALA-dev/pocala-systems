import time
import random
import re
import string
import json
import random
from inout.whisper_transcriber import transcribe_auto, transcribe_en
from inout.recorder import record_once
from inout.piper_output import speak_and_display
from clients.ollama_client import OllamaClient
from utils.extract_word import extract_topic
from utils.path_helper import get_resource_path
from utils.response_check import is_yes, is_no
from utils.ollama_context_builder import ChatContext

def normalize_answer(user_text, mode="mc"):
    """
    Normalisasi jawaban user.
    mode="mc"  -> multiple choice, ambil huruf A-D
    mode="short" -> short answer, kembalikan teks lower-case tanpa tanda baca
    """
    # Hilangkan tanda baca
    translator = str.maketrans("", "", string.punctuation)
    cleaned_text = user_text.translate(translator).strip()

    if mode == "mc":
        cleaned_lower = cleaned_text.lower()
        word_to_letter = {
            "a": "A", "ay": "A", "ei": "A",
            "b": "B", "bee": "B", "be": "B", "bi": "B",
            "c": "C", "see": "C", "sea": "C", "she": "C", "si": "C",
            "d": "D", "dee": "D", "di": "D", "de": "D"
        }
        # Cek langsung A-D
        match = re.search(r"\b([A-Da-d])\b", cleaned_lower, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        # Cek bentuk kata
        for token in cleaned_lower.split():
            if token in word_to_letter:
                return word_to_letter[token]
        return cleaned_text.upper()  # fallback huruf besar

    elif mode == "short":
        return cleaned_text.lower()

    return cleaned_text


def parse_question_and_answer(model_output):
    """
    Parsing hasil model menjadi:
    - question_text: teks pertanyaan tanpa pilihan & jawaban
    - options: list pilihan [ "A) ...", "B) ...", ... ]
    - correct_answer: string jawaban benar (misal 'D', atau 'D) Imperative mood')
    """
    lines = [line.strip() for line in model_output.strip().splitlines() if line.strip()]
    
    question_lines = []
    options = []
    correct_answer = None
    
    for line in lines:
        lower_line = line.lower()
        
        # Deteksi jawaban benar
        if lower_line.startswith("key answer") or lower_line.startswith("correct answer"):
            correct_answer = line.split(":", 1)[-1].strip()
        
        # Deteksi pilihan A-D
        elif re.match(r"^[A-D]\)", line, re.IGNORECASE):
            options.append(line)
        
        # Selain itu dianggap bagian pertanyaan
        else:
            question_lines.append(line)

    question_text = "\n".join(question_lines).strip()
    return question_text, options, correct_answer


def tanya_lanjut_question(lcd=None):
    speak_and_display(
        "Do you want another exercise? or change topic or type?",
        lang="en",
        lcd=lcd
    )
    while True:
        audio = record_once("ask_again_exercise.wav", lcd=lcd)
        if audio is None:
            speak_and_display("No audio detected. Please try again.", lang="en", lcd=lcd)
            continue
        reply = transcribe_auto(audio, lcd=lcd).lower()
        print(f"[USER REPLY]: {reply}")
        if is_no(reply) or any(word in reply for word in ["tidak", "enggak", "ga", "gak"]):
            speak_and_display("Exiting question mode. Goodbye!", lang="en", lcd=lcd)
            return "exit"
        elif is_yes(reply) or any(word in reply for word in ["ya", "lanjut", "boleh"]):
            return "continue"
        elif any(word in reply for word in ["change topic", "topic", "topik", "ganti topik", "topik baru"]):
            return "change_topic"
        elif any(word in reply for word in ["change type", "ganti tipe", "jenis baru", "type", "tipe", "time"]):
            return "change_type"
        elif any(word in reply for word in ["change both", "ganti semua", "new", "all", "bot", "everything"]):
            return "change_both"
        else:
            speak_and_display(
                "I didn't understand. Please say yes, no, or what you want to change.",
                lang="en",
                lcd=lcd
            )


def question_mode(lcd=None):
    """
    Mode latihan soal bahasa Inggris berbasis suara.

    Pengguna memilih topik dan tipe soal (pilihan ganda atau jawaban singkat),
    lalu menjawab pertanyaan melalui suara. Sistem membuat soal secara dinamis,
    memeriksa jawaban, memberikan umpan balik, dan menanyakan apakah ingin
    melanjutkan, mengganti topik, atau keluar.

    Args:
        lcd (LCDController, optional): Objek untuk menampilkan teks di LCD.
    """
    
    ollama = OllamaClient(model="gemma3:1b")
    context = ChatContext(max_messages=6)


    speak_and_display("Question function selected.", lang="en", lcd=lcd)
    topic = None
    question_type = None
    question_number = 1
    last_question = None
    last_correct_answer = None
    previous_questions = [] 
    
    # Load daftar topik dari file JSON
    topics_path = get_resource_path("resource", "predefined_topics.json")
    with open(topics_path, "r", encoding="utf-8") as f:
        predefined_topics = json.load(f)
        
    while True:
        # === Tanya apakah ingin pilih topik spesifik ===
        if topic is None:
            speak_and_display("Do you want to choose a specific topic?", lang="en", lcd=lcd)
            while True:
                audio = record_once("choose_topic.wav", lcd=lcd)
                if audio is None:
                    speak_and_display("No audio detected. Please try again.", lang="en", lcd=lcd)
                    continue
                reply = transcribe_auto(audio, lcd=lcd).lower()
                if is_yes(reply):
                    # Pilih topic manual
                    speak_and_display("Please say the topic you want to practice.", lang="en", lcd=lcd)
                    while True:
                        audio_topic = record_once("topic.wav", lcd=lcd)
                        if audio_topic is None:
                            speak_and_display("No audio detected. Please try again.", lang="en", lcd=lcd)
                            continue
                        raw_text = transcribe_en(audio_topic, lcd=lcd).strip()
                        topic = extract_topic(raw_text)
                        print(f"[TOPIC EXTRACTED]: {topic}")
                        if not topic:
                            speak_and_display("Sorry, I didn't catch the topic. Please try again.", lang="en", lcd=lcd)
                            continue
                        break
                    speak_and_display(f"topic chosen: {topic}", lang="en", lcd=lcd)
                    break
                elif is_no(reply):
                    # Pilih topic random dari daftar
                    topic = random.choice(predefined_topics)
                    print(f"[TOPIC RANDOMLY CHOSEN]: {topic}")
                    speak_and_display(f"Random topic chosen: {topic}", lang="en", lcd=lcd)
                    break
                else:
                    speak_and_display("Please say yes or no.", lang="en", lcd=lcd)
        
        # === Pilih tipe soal ===
        if question_type is None:
            speak_and_display("What type of question? Options or short answer?", lang="en", lcd=lcd)
            while True:
                audio = record_once(filename="type.wav", lcd=lcd)
                if audio is None:
                    speak_and_display("No audio detected. Please try again.", lang="en", lcd=lcd)
                    continue
                type_input = transcribe_en(audio, lcd=lcd).strip().lower()
                if any(w in type_input for w in ["option", "options", "multiple", "choice", "select", "action"]):
                    question_type = "multiple choice"
                    break
                elif any(w in type_input for w in ["short", "answer", "essay", "paragraph", "fill", "swear", "shard", "and"]):
                    question_type = "short answer"
                    break
                elif any(w in type_input for w in ["ulang", "repeat", "change", "back", "kembali", "topic"]):
                    topic = None
                    question_type = None
                    break
                speak_and_display("Unknown type. Please say options or short answer.", lang="en", lcd=lcd)
                
        if topic is None:
            continue
            
        # Bersihkan context lalu isi ringkasan soal lama
        context.clear(keep_system=True)
        for q in previous_questions:
            context.add_user_message(f"Previous question: {q},")

        # Buat soal
        if lcd:
            lcd.display_text(f"Generating question {question_number}...")

        if question_type == "multiple choice":
            prompt = (
                f"Question Number {question_number}.\n"
                f"Generate exactly ONE English multiple-choice question about the topic '{topic}'.\n"
                f"Avoid repeating any of the previous questions mentioned in chat history.\n"
                f"Include:\n"
                f"- Question text\n"
                f"- Four answer choices labeled A), B), C), D)\n"
                f"- Give the correct answer letter and text, starting with 'Correct Answer:'\n"
                f"Do not give explanation.\n"
                f"Output must contain only ONE question, not a list."
            )
        else:
            prompt = (
                f"Question Number {question_number}.\n"
                f"Generate exactly ONE English short-answer question about the topic '{topic}'.\n"
                f"Avoid repeating any of the previous questions mentioned in chat history.\n"
                f"Include:\n"
                f"- Question text without options\n"
                f"- Give the correct answer, starting with 'Correct Answer:'\n"
                f"Do not give explanation.\n"
                f"Output must contain only ONE question, not a list."
            )
            
        model_output = ollama.chat(prompt, context).replace("*", "")
        print(f"[RAW MODEL OUTPUT]:\n{model_output}")

        # Pisahkan soal & kunci jawaban
        question_text, options, last_correct_answer = parse_question_and_answer(model_output)
        last_question = question_text
        
        # Simpan ringkasan pertanyaan
        extracted_question_line = question_text.splitlines()[0] if question_text else ""
        previous_questions.append(extracted_question_line.strip())

        # Tampilkan pertanyaan
        speak_and_display(question_text, lang="en", lcd=lcd)
        time.sleep(0.5)

        # Tampilkan pilihan satu per satu (kalau ada)
        for opt in options:
            speak_and_display(opt, lang="en", lcd=lcd)
            time.sleep(0.3)  # jeda antar pilihan
    
        # Minta jawaban user
        speak_and_display("Please say your answer.", lang="en", lcd=lcd)
        while True:
            audio = record_once("answer.wav", lcd=lcd)
            if audio is None:
                speak_and_display("No audio detected. Please try again.", lang="en", lcd=lcd)
                continue
            raw_answer = transcribe_auto(audio, lcd=lcd).strip()
            if question_type == "multiple choice":
                answer = normalize_answer(raw_answer, mode="mc")
            else:
                answer = normalize_answer(raw_answer, mode="short")
            if answer:
                break
            speak_and_display("Sorry, I didn't catch your answer. Please try again.", lang="en", lcd=lcd)
            
        if lcd:
            lcd.flash_message(f"Your Answer {answer}", duration=2)
            
        # Evaluasi tanpa context
        if question_type == "multiple choice":
            eval_prompt = (
                "You are an English grammar teacher.\n"
                f"Question:\n{last_question}\n"
                + "\n".join(options) + "\n\n"
                f"Correct Answer: {last_correct_answer}\n"
                f"User Answer: {answer}\n\n"
                "Evaluate if the user's answer is correct or incorrect\n"
                "Respond in Indonesian with:\n"
                "[Penilaian] <singkat benar/salah>\n"
                "[Alasan] <penjelasan singkat dan jawaban yang benar>"
            )
        else:  # short answer
            eval_prompt = (
                "You are an English grammar teacher.\n"
                f"Question:\n{last_question}\n\n"
                f"Correct Answer: {last_correct_answer}\n"
                f"User Answer: {answer}\n\n"
                "Evaluate if the user's answer has the SAME MEANING as the correct answer, "
                "even if the wording is different.\n"
                "mark as almost correct if the answer is a synonym, paraphrase, or "
                "slightly different wording with the same meaning.\n"
                "Respond in Indonesian with:\n"
                "[Penilaian] <singkat benar/hampir benar/salah>\n"
                "[Alasan] <penjelasan singkat dan jawaban yang benar>"
            )

        feedback = ollama.chat([{"role": "user", "content": eval_prompt}]).replace("*", "")
        print(f"[EVALUATION FEEDBACK]: {feedback}")

        if "[Penilaian]" in feedback and "[Alasan]" in feedback:
            penilaian, alasan = feedback.split("[Alasan]", 1)
            speak_and_display(penilaian.replace("[Penilaian]", "").strip(), lang="id", lcd=lcd)
            speak_and_display(alasan.strip(), lang="id", mode="scroll", lcd=lcd)
        else:
            speak_and_display(feedback, lang="id", mode="scroll", lcd=lcd)

        # Tanya lanjut
        keputusan = tanya_lanjut_question(lcd=lcd)
        if keputusan == "exit":
            break
        elif keputusan == "continue":
            question_number += 1
        elif keputusan == "change_topic":
            topic = None
            question_number = 1
            previous_questions.clear()
        elif keputusan == "change_type":
            question_type = None
            question_number = 1
            previous_questions.clear()
        elif keputusan == "change_both":
            topic = None
            question_type = None
            question_number = 1
            previous_questions.clear()

# Mode untuk memeriksa tata bahasa menggunakan Google Cloud.
from inout.gcp_transcriber import transcribe_en, transcribe_auto
from clients.gcp_client import gcp_gemini_generate, gemini_model
from inout.recorder import record_once
from inout.gcp_output import speak_and_display
from utils.response_check import is_yes, is_no


def tanya_ulang_grammar(lcd=None):
    """Menanyakan kepada pengguna apakah ingin memeriksa kalimat lain."""
    speak_and_display(
        "Do you want to check another sentence?", lang="en", lcd=lcd
    )

    while True:
        audio = record_once(filename="ask_again_grammar.wav", lcd=lcd)
        if not audio:
            continue

        reply = transcribe_auto(audio, lcd=lcd).lower()
        print(f"[USER REPLY]: {reply}")

        if is_no(reply):
            speak_and_display(
                "Exiting grammar function. Goodbye!", lang="en", lcd=lcd
            )
            return False
        elif is_yes(reply):
            return True
        else:
            speak_and_display(
                "I didn't understand. Please say yes or no.",
                lang="en", lcd=lcd
            )


def grammar_mode(lcd=None):
    """Mode untuk memeriksa dan memperbaiki tata bahasa
    menggunakan Google Gemini.
    """
    if not gemini_model:
        speak_and_display(
            "Grammar mode cannot be started. Gemini API key is missing.",
            "en", lcd
        )
        return

    speak_and_display("Grammar function selected.", lang="en", lcd=lcd)

    while True:
        speak_and_display(
            "Please say a sentence you want me to check.",
            lang="en", lcd=lcd
        )

        # Loop sampai dapat input yang valid
        while True:
            audio = record_once(filename="grammar_input.wav", lcd=lcd)
            if not audio:
                speak_and_display(
                    "No audio detected. Please try again.",
                    lang="en", lcd=lcd
                )
                continue

            sentence = transcribe_en(audio, lcd=lcd).strip()
            if not sentence:
                speak_and_display(
                    "Sorry, I didn't catch that. Please try again.",
                    lang="en", lcd=lcd
                )
                continue
            break

        print(f"[TRANSCRIBED INPUT]: {sentence}")
        if lcd:
            lcd.flash_message(f"Input: {sentence}", duration=3)
            lcd.display_text("Checking grammar...")

        prompt = (
            f"Perbaiki tata bahasa dari kalimat: \"{sentence}\"\n"
            "Format:\n"
            "[Corrected] kalimat yang benar in English.\n"
            "[Explanation] penjelasan singkat apa yang diperbaiki "
            "dalam Bahasa Indonesia."
        )

        try:
            result = gcp_gemini_generate(prompt).strip().replace("*", "")
            print(f"[GEMINI RESULT]: {result}")
        except Exception as e:
            speak_and_display(
                f"Error generating response: {e}",
                lang="en", lcd=lcd
            )
            continue

        # Parsing lebih toleran
        corrected = ""
        explanation = ""
        try:
            if "[Corrected]" in result:
                corrected = result.split("[Corrected]", 1)[1]
                if "[Explanation]" in corrected:
                    corrected = corrected.split(
                        "[Explanation]", 1
                    )[0]
                corrected = corrected.strip()

            if "[Explanation]" in result:
                explanation = result.split(
                    "[Explanation]", 1
                )[1].strip()

            # Fallback kalau parsing gagal
            if not corrected:
                corrected = "I couldn't extract the corrected sentence."
            if not explanation:
                explanation = "Tidak ada penjelasan yang tersedia."
        except Exception as e:
            corrected = "Parsing error."
            explanation = f"Gagal parsing hasil: {e}"

        # Tampilkan hasil
        speak_and_display(
            f"Corrected sentence: {corrected}",
            lang="en", mode="scroll", lcd=lcd
        )
        if explanation:
            speak_and_display(
                f"Penjelasan: {explanation}",
                lang="id", mode="scroll", lcd=lcd
            )

        if not tanya_ulang_grammar(lcd=lcd):
            break

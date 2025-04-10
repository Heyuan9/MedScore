"""Prompts"""

MEDSCORE_PROMPT = """You are a medical expert in evaluating how factual a medical sentence is. You break down a sentence into as many facts as possible. The facts should be objective and verifiable against reliable external information such as Wikipedia and PubMed. All subjective personal experiences (\\\"I was or someone did\\\") and personal narratives (stating a past event) are not verifiable and should not be included in the fact list. Facts should be situated within conditions in the sentence. Suggestions (e.g. \\\"I recommend or Your doctor suggest\\\") and opinions (e.g. \\\"I think\\\") should be transformed into objective facts by removing subjective words and pronouns to only retain the core information that can be verified. Imperative instructions (\\\"do something\\\") should be transformed into declarative facts (\\\"doing something is helpful for some conditions\\\").

If there is an overly specific entity such as \\\"Your partner\\\" or vague references (pronouns, this or that) in the fact, replace it with a general phrase with conditional modifiers using information in the provided context (e.g. \\\"People in some conditions\\\"). Each fact should be verifiable on its own and require no additional context. Do not add additional information outside of the sentence and context. You do not need to justify what you extract.

If there is no verifiable fact in the sentence, please write \\\"No verifiable claim\\\".

Here are some examples:

Context: I spoke to your doctor and they wanted to address your concerns about tetanus. Since you've had your primary tetanus shots as a child, you don't need immunoglobulin (IGG) shots, and they were actually unnecessary during your last visit. \n\n Considering your tetanus vaccine expired in 2020 and you've got a dirty wound from the Spartan race, your doctor recommends getting a tetanus booster vaccine as soon as possible. They also mentioned that you were due for a booster anyway since it's been more than 3 years since your last vaccine.\n\nYour doctor is a bit puzzled as to why you were given IGG shots instead of a vaccine during your last visit, but that's not a concern for now. They just want to make sure you get the booster vaccine to be on the safe side. It's best to schedule an appointment for the booster vaccine as soon as possible to avoid any potential risks.
Please breakdown the following sentence into independent facts: I spoke to your doctor and they wanted to address your concerns about tetanus.
Facts:
- No verifiable claim

Context: I spoke to your doctor, and they expressed concerns about the safety of using anabolic steroids, particularly in combination with the medications your partner is already taking for Addison's disease. The doctor noted that while these substances may have positive effects on muscle and bone health, they also carry significant risks and potential side effects.\n\nThe doctor mentioned that the anabolic cycle your partner is on is quite intense and requires careful monitoring for potential issues such as infertility, mood swings, and problems related to weight gain, including snoring and possible sleep apnea. They also emphasized the importance of considering the long-term effects of using these substances, particularly when they are stopped.\n\nThe doctor's primary concern is that your partner's underlying condition, Addison's disease, may not significantly complicate things if well-treated, but it could become an issue when the anabolic cycle is stopped. They strongly advise that your partner consult with a medical professional, ideally their endocrinologist, to discuss the potential risks and consequences of using these substances, especially given their pre-existing condition.\n\nIt's essential to have an open and honest conversation with a healthcare professional to ensure your partner's safety and well-being. I would encourage you to support your partner in seeking medical advice, and I'm happy to facilitate a discussion with their doctor if needed.
Please breakdown the following sentence into independent facts: The doctor noted that while these substances may have positive effects on muscle and bone health, they also carry significant risks and potential side effects.
Facts:
- Anabolic steroids may have positive effects on muscle health.
- Anabolic steroids may have positive effects on bone health.
- Anabolic steroids may also carry significant risks.
- Anabolic steroids may carry potential side effects.

Context: I spoke to your doctor and they would like to know more about the specific tests you are interested in having done. They mentioned that their willingness to order these tests may depend on what you are asking for. If the tests are rare or uncommon, they may recommend that you see a specialist who is more familiar with those types of tests and their results. Your doctor wants to make sure that any tests that are ordered are properly interpreted and that you receive the best possible care. Could you please provide more information about the tests you are interested in having done?
Please breakdown the following sentence into independent facts: If the tests are rare or uncommon, they may recommend that you see a specialist who is more familiar with those types of tests and their results. 
Facts:
- If the tests are rare or uncommon, seeing a specialist is helpful.
- The specialist is more familiar with rare or uncommon types of tests.
- The specialist is more familiar with the results of rare or uncommon tests.

Context: Hi there,\n\nI spoke to your doctor and they wanted to reassure you that getting the immunoglobulin shot within 38 hours of the potential exposure is still considered a safe timeframe. They mentioned that as long as you received the shot before 7 days from the incident, you should be okay.\n\nYour doctor recommends that you follow up on the scheduled dates for your remaining rabies shots. They also wanted to remind you that rabies has a relatively long incubation period, typically ranging from 1-3 months, before symptoms start to show. This means that even if you were bitten by an infected bat, you would likely have developed immunity by the time symptoms appear.\n\nPlease try to take care of yourself and manage your anxiety during this time. If you have any further concerns or questions, don't hesitate to reach out.\n\nBest regards,\n\n[Your Doctor's Name]
Please breakdown the following sentence into independent facts: They also wanted to remind you that rabies has a relatively long incubation period, typically ranging from 1-3 months, before symptoms start to show.
Facts:
- Rabies has a relatively long incubation period.
- The incubation period for rabies typically ranges from 1-3 months.
- Rabies symptoms start to show after the incubation period.

Context: I spoke to your doctor and they wanted to thank you for your interest in creating a language course to help physicians better communicate with patients who speak different languages. \n\nThey mentioned that while language barriers can contribute to the \\\"revolving door syndrome,\\\" it's just one of many factors. Other important factors include education, home support, medication noncompliance, and lack of primary care. \n\nIn terms of a language course, your doctor thinks that Duolingo is a good option. However, they noted that it's challenging for doctors to find the time to learn multiple languages, as there are many languages spoken by patients in their area, including Spanish, Hmong, Chinese, and Polish. They also mentioned that many Spanish-speaking patients have some knowledge of English or have family members who are fluent in English.\n\nYour doctor didn't specify a preferred medium for the course, but they seemed to appreciate the idea of a convenient and accessible program. They also didn't provide specific vocabulary recommendations, but it's likely that a course focused on medical terminology and common patient interactions would be most useful.
Please breakdown the following sentence into independent facts: However, they noted that it's challenging for doctors to find the time to learn multiple languages, as there are many languages spoken by patients in their area, including Spanish, Hmong, Chinese, and Polish.
Facts:
- It is challenging for doctors to find the time to learn multiple languages.
- Many languages are spoken by patients in doctors' area.
- Spanish is one of the languages spoken by patients in doctors' area.
- Hmong is one of the languages spoken by patients in doctors' area.
- Chinese is one of the languages spoken by patients in doctors' area.
- Polish is one of the languages spoken by patients in doctors' area.

Context: I spoke to your doctor and they think that you just need a bit more time to recover from your surgery. They noted that your usual lifestyle is quite sedentary, and having surgery can be a significant strain on your body, similar to intense physical activity. This, combined with your extreme anxiety, which can cause muscle tension, is likely contributing to your soreness. \n\nAs long as you don't develop a fever and your wounds show no signs of infection, your doctor believes that there's not much more the hospital can do for you that you can't do at home. Their advice is to focus on meeting your daily needs, such as eating, drinking, and using the bathroom, and not to worry too much about the soreness right now. \n\nOnce the soreness starts to subside, they recommend that you try to gradually increase your activities, starting with small steps like sitting in a chair, standing, and eventually walking, until you're back to your normal self.
Please breakdown the following sentence into independent facts: Once the soreness starts to subside, they recommend that you try to gradually increase your activities, starting with small steps like sitting in a chair, standing, and eventually walking, until you're back to your normal self.
Facts:
- Once the soreness starts to subside, trying to gradually increase activities is helpful.
- People with soreness should start with small steps.
- Small steps for people with soreness include sitting in a chair.
- Small steps for people with soreness include standing.
- Small steps for people with soreness include walking.
- Gradually increasing activities helps people with soreness return to normal self.

Context: I spoke to your doctor and they wanted to address the questions you have regarding your loved one's complications from COVID-19. The doctor believes that the likely sequence of events is that the COVID-19 infection led to demand ischemia, which in turn caused the myocardial infarction (MI). \n\nThe doctor thinks that both the transfer hospital and the receiving hospital properly prioritized the patient's issues and treated the most life-threatening condition, the acute MI, first. Unfortunately, the patient had many underlying risk factors that made them more susceptible to severe illness from any infection, not just COVID-19.\n\nRegarding the patient going without clopidogrel for 10 days, the doctor agrees that this may have contributed to the MI, although it's impossible to determine the exact extent of its impact.\n\nAs for the new diagnoses of congestive heart failure (CHF), chronic obstructive pulmonary disease (COPD), and acute respiratory failure, the doctor did not provide a specific prognosis. However, they did mention that the patient's underlying health conditions and the severity of their illness have made their situation more challenging.\n\nThe doctor also believes that initiating COVID-19 treatment at the time of presentation may not have significantly altered the course of the patient's illness.\n\nPlease let us know if you have any further questions or concerns.
Please breakdown the following sentence into independent facts: However, they did mention that the patient's underlying health conditions and the severity of their illness have made their situation more challenging. 
Facts:
- The patient's underlying health conditions makes the acute myocardial infarction situation more challenging.
- The severity of the patient's illness makes the acute myocardial infarction situation more challenging.
- The patient's acute myocardial infarction situation is challenging.
  
Context: I spoke to your doctor and they wanted to address your concerns regarding the leakage you experienced after your bowel surgery in 2013. According to them, it is possible for an abnormal connection to form between your bowel and your bladder or vagina, which is known as a fistula. This could potentially cause the leakage of substances from your bowel into your urinary tract or vagina.\n\nYour doctor recommends reviewing the notes from your second surgery to understand the nature of the repairs that were performed. This information may help clarify what happened in your specific case.\n\nRegarding your concerns about the quality of care you received from your initial surgeon, your doctor advises that medical malpractice is a complex issue that depends on many factors, including the specific circumstances of your case and the laws in your location. If you're interested in exploring this further, they recommend consulting with a lawyer who can provide guidance on whether you have a valid case.\n\nPlease let us know if you have any further questions or concerns, and we'll be happy to help.
Please breakdown the following sentence into independent facts: Please let us know if you have any further questions or concerns, and we'll be happy to help.
Facts:
- No verifiable claim
"""

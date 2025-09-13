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
  
Context: I spoke to your doctor and they wanted to address your concerns regarding the leakage you experienced after your bowel surgery in 2013. According to them, it is possible for an abnormal connection to form between your bowel and your bladder or vagina, which is known as a fistula. This could potentially cause the leakage of substances from your bowel into your urinary tract or vagina.\n\nYour doctor recommends reviewing the notes from your second surgery to understand the nature of the repairs that were performed. This information may help clarify what happened in your specific case.\n\nRegarding your concerns about the quality of care you received from your initial surgeon, your doctor advises that medical malpractice is a complex issue that depends on many factors, including the specific circumstances of your case and the laws in your location. If you're interested in exploring this further, they recommend consulting with a lawyer who can provide guidance on whether you have a valid case.\n\nPlease let us know if you have any further questions or concerns, and we'll be happy to help.
Please breakdown the following sentence into independent facts: Please let us know if you have any further questions or concerns, and we'll be happy to help.
Facts:
- No verifiable claim

Context: Dear Patient,\n\nI spoke to your doctor and they wanted to address your concerns about the sharp pain you've been experiencing above your left eyebrow when exposed to strong wind. After reviewing your symptoms, they think that trigeminal neuralgia could be a possible cause of your pain. \n\nThey considered cluster headaches as well, but they believe it's less likely in your case because cluster headaches typically occur at the same time every day, last for several days in a row, and involve pain behind or around the entire eye on one side.\n\nYour doctor would like to discuss this further with you and explore the possibility of trigeminal neuralgia being the cause of your pain. They recommend that you schedule a follow-up appointment to discuss your symptoms in more detail and determine the best course of action.\n\nPlease let us know if you have any questions or concerns before your appointment.\n\nBest regards,\n[Your Name]\nOn behalf of [Doctor's Name]
Please breakdown the following sentence into independent facts: Dear Patient,\n\nI spoke to your doctor and they wanted to address your concerns about the sharp pain you've been experiencing above your left eyebrow when exposed to strong wind.
Facts:
- No verifiable claim

Context: I spoke to your doctor, and they recommended that you visit a pharmacy to get an over-the-counter anti-nausea medication, such as Dramamine (also known as Gravol), to help alleviate your symptoms. They would like to know how you're feeling now, 4 hours after your initial message, to assess if your condition is improving or if further action is needed. If your symptoms persist, your doctor may want to investigate further to determine the cause of your discomfort. Please let us know your current status so we can provide further guidance.
Please breakdown the following sentence into independent facts: They would like to know how you're feeling now, 4 hours after your initial message, to assess if your condition is improving or if further action is needed.
Facts:
- No verifiable claim

Context: I spoke to your doctor and they wanted to reassure you that, given you are not sexually active and have never had penetrative intercourse, it is not possible for you to be pregnant. They understand that you have been experiencing anxiety and pregnancy scares, and they think it's a great idea for you to see a psychologist to help you manage these feelings.\n\nRegarding your symptoms, your doctor believes that starting a stable contraceptive therapy, such as the pill or other hormonal methods, could be helpful in regulating your periods and alleviating some of the symptoms you're experiencing. They think this could be a useful approach to help you feel better and more in control of your situation.\n\nPlease keep in mind that your upcoming ultrasound will likely provide more insight into what's going on with your body, and your doctor will be able to discuss the results with you and determine the best course of action.
Please breakdown the following sentence into independent facts: They understand that you have been experiencing anxiety and pregnancy scares, and they think it's a great idea for you to see a psychologist to help you manage these feelings.
Facts:
- Seeing a psychologist can help manage feelings of anxiety and pregnancy scares.
"""


MEDSCORE_Ablation_PROMPT = """You are a medical expert in evaluating how factual a medical sentence is. You break down a sentence into as many facts as possible. The facts should be objective and verifiable against reliable external information such as Wikipedia and PubMed. All subjective personal experiences (\\\"I was or someone did\\\") and personal narratives (stating a past event) are not verifiable and should not be included in the fact list. Facts should be situated within conditions in the sentence. Suggestions (e.g. \\\"I recommend or Your doctor suggest\\\") and opinions (e.g. \\\"I think\\\") should be transformed into objective facts by removing subjective words and pronouns to only retain the core information that can be verified. Imperative instructions (\\\"do something\\\") should be transformed into declarative facts (\\\"doing something is helpful for some conditions\\\").

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

FACTSCORE_PROMPT = f"""Please breakdown the following sentence into independent facts: He made his acting debut in the film The Moon is the Sun’s Dream (1992), and continued to appear in small and supporting roles throughout the 1990s. 
- He made his acting debut in the film. 
- He made his acting debut in The Moon is the Sun’s Dream. 
- The Moon is the Sun’s Dream is a film. 
- The Moon is the Sun’s Dream was released in 1992. 
- After his acting debut, he appeared in small and supporting roles. 
- After his acting debut, he appeared in small and supporting roles throughout the 1990s. 

Please breakdown the following sentence into independent facts: He is also a successful producer and engineer, having worked with a wide variety of artists, including Willie Nelson, Tim McGraw, and Taylor Swift. 
- He is successful. 
- He is a producer. 
- He is a engineer. 
- He has worked with a wide variety of artists. 
- Willie Nelson is an artist. 
- He has worked with Willie Nelson. 
- Tim McGraw is an artist. 
- He has worked with Tim McGraw. 
- Taylor Swift is an artist. 
- He has worked with Taylor Swift. 

Please breakdown the following sentence into independent facts: In 1963, Collins became one of the third group of astronauts selected by NASA and he served as the back-up Command Module Pilot for the Gemini 7 mission. 
- Collins became an astronaut. 
- Collins became one of the third group of astronauts. 
- Collins became one of the third group of astronauts selected. 
- Collins became one of the third group of astronauts selected by NASA. 
- Collins became one of the third group of astronauts selected by NASA in 1963. 
- He served as the Command Module Pilot. 
- He served as the back-up Command Module Pilot. 
- He served as the Command Module Pilot for the Gemini 7 mission. 

Please breakdown the following sentence into independent facts: In addition to his acting roles, Bateman has written and directed two short films and is currently in development on his feature debut. 
- Bateman has acting roles. 
- Bateman has written two short films. 
- Bateman has directed two short films. 
- Bateman has written and directed two short films. 
- Bateman is currently in development on his feature debut. 

Please breakdown the following sentence into independent facts: Michael Collins (born October 31, 1930) is a retired American astronaut and test pilot who was the Command Module Pilot for the Apollo 11 mission in 1969. 
- Michael Collins was born on October 31, 1930. 
- Michael Collins is retired. 
- Michael Collins is an American. 
- Michael Collins was an astronaut. 
- Michael Collins was a test pilot. 
- Michael Collins was the Command Module Pilot. 
- Michael Collins was the Command Module Pilot for the Apollo 11 mission. 
- Michael Collins was the Command Module Pilot for the Apollo 11 mission in 1969. 

Please breakdown the following sentence into independent facts: He was an American composer, conductor, and musical director. 
- He was an American. 
- He was a composer. 
- He was a conductor. 
- He was a musical director. 

Please breakdown the following sentence into independent facts: She currently stars in the romantic comedy series, Love and Destiny, which premiered in 2019. 
- She currently stars in Love and Destiny.
- Love and Destiny is a romantic comedy series. 
- Love and Destiny premiered in 2019. 

Please breakdown the following sentence into independent facts: During his professional career, McCoy played for the Broncos, the San Diego Chargers, the Minnesota Vikings, and the Jacksonville Jaguars. 
- McCoy played for the Broncos. 
- McCoy played for the Broncos during his professional career. 
- McCoy played for the San Diego Chargers. 
- McCoy played for the San Diego Chargers during his professional career. 
- McCoy played for the Minnesota Vikings. 
- McCoy played for the Minnesota Vikings during his professional career. 
- McCoy played for the Jacksonville Jaguars. 
- McCoy played for the Jacksonville Jaguars during his professional career.
"""

INTERNAL_KNOWLEDGE_PROMPT = f"""You are an assistant who verifies whether a claim from a medical response is True. You should rely exclusively on your own knowledge and always output 'True' or 'False' first. If there is not enough context or you are unable to verify the claim, then output 'False'."""

DND_PROMPT = """Ambiguity Criteria: Ambiguity manifests in diverse forms, including:
- Similar names denoting distinct entities.
- Varied interpretations stemming from insufficient information.
- Multiple understandings arising from vague or unclear information.

Instructions:
- You are given a paragraph, and one sentence from the paragraph to decompose and decontextualize.
- First decompose the sentence into subclaims. Only use information from the sentence, and do not add any external information.
- Then using those subclaims, write a decontextualized version of each subclaim.
- In the decontextualized version, include all necessary information to disambiguate any entities or events in the subclaim using the ambiguity criteria above.
- In the decontextualized version, only use information from the paragraph. Do not add any external information.
- Provide an explanation of what ambiguities need to be resolved

Format your response as a combination of decomposition and a dictionary with pairs of context and subclaims:
##PARAGRAPH##: <paragraph>
##SENTENCE##: <sentence>
##SUBCLAIMS##:
<list-of-subclaims>
##EXPLANATION##:
<explanations>
##CONTEXT-SUBCLAIM PAIRS##:
[
    {"subclaim": <subclaim1>, "decontextualized": <context1>},
    {"subclaim": <subclaim2>, "decontextualized": <context2>},
    ...
]

Example 1:
##PARAGRAPH##: Michael Collins (born October 31, 1930) is a retired American astronaut and test pilot who was the Command Module Pilot for the Apollo 11 mission in 1969. He orbited the Moon in the command module Columbia while Neil Armstrong and Buzz Aldrin made their historic landing. Born in Rome, Italy, Collins graduated from the U.S. Military Academy in 1952, joining a family tradition of military service, and went on to become a test pilot in the U.S. Air Force. Selected as an astronaut in 1963, he flew two space missions, Gemini 10 in 1966 and Apollo 11 in 1969, making him one of only 24 people to travel to the Moon. Collins was an accomplished astronaut, becoming the fourth person to conduct a spacewalk and the first to perform multiple spacewalks. After leaving NASA in 1970, he served as Assistant Secretary of State for Public Affairs, later directing the National Air and Space Museum. He also held senior roles at the Smithsonian and in private aerospace, eventually founding his own consulting firm. Collins and his Apollo 11 crewmates received the Presidential Medal of Freedom in 1969 and the Congressional Gold Medal in 2011.
##SENTENCE##: Michael Collins (born October 31, 1930) is a retired American astronaut and test pilot who was the Command Module Pilot for the Apollo 11 mission in 1969.
##SUBCLAIMS##:
- Michael Collins was born in October.
- Michael Collins was born on the 31st day of a month.
- Michael Collins was born in 1930.
- Michael Collins is retired.
- Michael Collins is American.
- Michael Collins was an astronaut.
- Michael Collins was a test pilot.
- Michael Collins participated in the Apollo 11 mission.
- Michael Collins's participation in the Apollo 11 mission occurred in 1969.
- The Apollo 11 mission was active in 1969.
- The day of Michael Collins's birth occurred before his year of participation in the Apollo 11 mission.
- The Apollo 11 mission had a Command Module Pilot.
- Michael Collins's role in the Apollo 11 mission was as the Command Module Pilot.
##EXPLANATION##:
"Michael Collins" needs to be disambiguated as the astronaut associated with the Apollo 11 mission to distinguish him from other potential individuals with similar names.
##CONTEXT-SUBCLAIM PAIRS##:
[
    {"subclaim": "Michael Collins was born in October.", "decontextualized": "Michael Collins, the retired American astronaut and test pilot, was born in October."},
    {"subclaim": "Michael Collins was born on the 31st day of a month.", "decontextualized": "Michael Collins, the retired American astronaut and test pilot, was born on the 31st day of a month."},
    {"subclaim": "Michael Collins was born in 1930.", "decontextualized": "Michael Collins, the retired American astronaut and test pilot, was born in 1930."},
    {"subclaim": "Michael Collins is retired.", "decontextualized": "Michael Collins, the retired American astronaut and test pilot, is retired."},
    {"subclaim": "Michael Collins is American.", "decontextualized": "Michael Collins, the American astronaut, is American."},
    {"subclaim": "Michael Collins was an astronaut.", "decontextualized": "Michael Collins, the retired American astronaut and Command Module Pilot for the Apollo 11 mission, was an astronaut."},
    {"subclaim": "Michael Collins was a test pilot.", "decontextualized": "Michael Collins, the retired American astronaut and test pilot, was the Command Module Pilot for the Apollo 11 mission in 1969."},
    {"subclaim": "Michael Collins participated in the Apollo 11 mission.", "decontextualized": "Michael Collins, the retired American astronaut and test pilot, participated in the Apollo 11 mission."},
    {"subclaim": "Michael Collins's participation in the Apollo 11 mission occurred in 1969.", "decontextualized": "Michael Collins's participation in the Apollo 11 mission as the Command Module Pilot occurred in 1969."},
    {"subclaim": "The Apollo 11 mission was active in 1969.", "decontextualized": "The Apollo 11 mission, which involved human spaceflight to the Moon, was active in 1969."},
    {"subclaim": "The day of Michael Collins's birth occurred before his year of participation in the Apollo 11 mission.", "decontextualized": "The day of Michael Collins's birth on October 31, 1930, occurred before his year of participation in the Apollo 11 mission."},
    {"subclaim": "The Apollo 11 mission had a Command Module Pilot.", "decontextualized": "The Apollo 11 mission had Michael Collins as its Command Module Pilot."},
    {"subclaim": "Michael Collins's role in the Apollo 11 mission was as the Command Module Pilot.", "decontextualized": "Michael Collins's role in the Apollo 11 mission was as the Command Module Pilot."}
]

Example 2:
##PARAGRAPH##: Stephen Miller (born August 23, 1985) is an American political advisor who served as a senior advisor for policy and director of speechwriting to President Donald Trump. Miller has been described as the architect of Trump's controversial immigration policies, and has previously worked for Alabama Senator Jeff Sessions on immigration issues. Miller was instrumental in shaping several of Trump's key policies, including the travel ban, a reduction in refugee admissions, and family separations at the border. He began his career in communications roles for conservative legislators, including Senators Jeff Sessions, Michele Bachmann, and John Shadegg. As Trump's speechwriter, Miller helped draft the inaugural address and served as a trusted advisor from the early days of the administration. He also played a significant role in the resignation of Secretary of Homeland Security Kirstjen Nielsen, whom he deemed insufficiently strict on immigration. As a White House spokesperson, Miller made several unsubstantiated claims about election fraud and promoted content from white nationalist sources, leading to his inclusion on the Southern Poverty Law Center's list of extremists.
##SENTENCE##: Miller has been described as the architect of Trump's controversial immigration policies, and has previously worked for Alabama Senator Jeff Sessions on immigration issues.
##SUBCLAIMS##:
- Miller has been described.
- Miller has been described as an architect.
- Miller has been described as an architect of Trump's controversial immigration policies.
- Trump has immigration policies.
- Trump's immigration policies are controversial.
- Miller worked for Jeff Sessions.
- Jeff Sessions is a Senator.
- Jeff Sessions represents Alabama.
- Miller worked on immigration issues.
- Miller's work for Jeff Sessions involved immigration issues.
##EXPLANATION##:
"Miller" needs to be disabiguated as Stephen Miller, a political advisor for Donald Trump, to avoid confusion with other individuals with the same name. Clarify that "Trump's immigration policies" refers specifically to policies developed during Donald Trump's presidency, as "Trump" alone may be ambiguous in a different context.
##CONTEXT-SUBCLAIM PAIRS##:
[
    {"subclaim": "Miller has been described.", "decontextualized": "Miller, the architect of Trump's controversial immigration policies, has been described."},
    {"subclaim": "Miller has been described as an architect.", "decontextualized": "Miller, who has been described as the architect of Trump's controversial immigration policies, has been described as an architect."},
    {"subclaim": "Miller has been described as an architect of Trump's controversial immigration policies.", "decontextualized": "Stephen Miller has been described as an architect of Trump's controversial immigration policies."},
    {"subclaim": "Trump has immigration policies.", "decontextualized": "Donald Trump has immigration policies."},
    {"subclaim": "Trump's immigration policies are controversial.", "decontextualized": "Donald Trump's immigration policies are controversial."},
    {"subclaim": "Miller worked for Jeff Sessions.", "decontextualized": "Miller, the architect of Trump's controversial immigration policies, worked for Jeff Sessions."},
    {"subclaim": "Jeff Sessions is a Senator.", "decontextualized": "Jeff Sessions is a Senator from Alabama."},
    {"subclaim": "Jeff Sessions represents Alabama.", "decontextualized": "Jeff Sessions represents the state of Alabama."},
    {"subclaim": "Miller worked on immigration issues.", "decontextualized": "Miller, the architect of Trump's controversial immigration policies, worked on immigration issues."},
    {"subclaim": "Miller's work for Jeff Sessions involved immigration issues.", "decontextualized": "Stephen Miller's work for Jeff Sessions involved immigration issues."}
]

Your task:
##PARAGRAPH##: [paragraph]
##SENTENCE##: [sentence]
##SUBCLAIMS##:"""


import * as i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const kr = {
    TITLE: "차차, 아이들의 마음을 읽어주는 AI",
    LANGUAGE_NAME: "한국어",
    SIGN_IN: {
        ERROR:{
            SESSION_ID: "세션 아이디는 공백 없는 대소문자와 숫자, 하이픈, 언더바만 가능해."
        },
        LANG: "언어",
        SESSION_NAME: "세션 이름",
        USER_NAME_PLACEHOLDER: "너의 이름은 뭐야? (성 빼고)",
        USER_AGE_PLACEHOLDER: "몇 살이야?",
        START: "대화 시작하기!"
    },
    SHARE: {
        SAVE: "CSV로 저장"
    },
    CHAT: {
        PROCESSING: "할 말을 생각 중이야. 잠시만 기다려줘!",
        INPUT_PLACEHOLDER: "나에게 할 말을 입력해줘!",
        SHARE_LINK: "링크 공유하기",
        LINK_COPIED: "링크가 클립보드에 복사되었습니다.",
        CONFIRM_REGEN_LAST_MESSAGE: "차차의 마지막 메시지를 다시 요청할래?",
        RESET_SESSION: "대화 종료하기",
        CONFIRM_RESET_SESSION: "현재 대화를 종료하고 초기 화면으로 돌아가시겠습니까?"
    },
    EMOTION_PICKER: {
        ERROR: {
            NOTHING_SELECTED: "하나 이상의 감정을 선택해야 해!"
        },
    },

    SESSION_INFO: {
        SESSION: "세션",
        PROFILE_FORMAT: "{name}, {age}세"
    },

    LABEL: {
        NEXT: "다음",
        SEND: "보내기",
        YES: "예",
        NO: "아니요",
    }
}

const en = {
    LANGUAGE_NAME: "English",
    TITLE: "Chacha, AI that reads children's minds",
    SIGN_IN: {
        ERROR:{
            SESSION_ID: "Only letters, numbers, hyphens, and underscores can be used. No spaces, okay?"},
        LANG: "Language",
        SESSION_NAME: "What's the session name?",
        USER_NAME_PLACEHOLDER: "What's your first name?",
        USER_AGE_PLACEHOLDER: "How old are you?",
        START: "Let's Chat!"
    },
    SHARE: {
        SAVE: "Save as CSV"
    },
    CHAT: {
        PROCESSING: "Thinking... Hang on!",
        INPUT_PLACEHOLDER: "Type what you want to say here!",
        SHARE_LINK: "Share Link",
        LINK_COPIED: "Link copied! You can paste it now.",
        CONFIRM_REGEN_LAST_MESSAGE: "Want Chacha to say that again differently?",
        RESET_SESSION: "End Session",
        CONFIRM_RESET_SESSION: "Are you sure you want to end the session?"
    },
    EMOTION_PICKER: {
        ERROR: {
            NOTHING_SELECTED: "You should check one or two emotions."
        },
    },

    SESSION_INFO: {
        SESSION: "Session",
        PROFILE_FORMAT: "{name}, {age} years old"
    },

    LABEL: {
        NEXT: "Next",
        SEND: "Send",
        YES: "Yes",
        NO: "No",
    }
}

export const LANGUAGE_LIST = ["kr", "en"]

i18n.use(initReactI18next)
    .init({
        resources: {
            en: {
                translation: en
            },
            kr: {
                translation: kr
            }
        },
        lng: 'kr',

        interpolation: {
            escapeValue: false
        }
    })

export default i18n;
import LanguageIcon from "@heroicons/react/20/solid/LanguageIcon"
import { useCallback } from "react"
import { useTranslation } from "react-i18next"
import { LANGUAGE_LIST } from "src/i18n"

export const LanguageSelector = (props: {
    className?: string
}) => {

    const [t, i18n] = useTranslation()

    const onLanguageButtonClick = useCallback(()=>{
        const currentLangIndex = LANGUAGE_LIST.indexOf(i18n.language)
        i18n.changeLanguage(LANGUAGE_LIST[(currentLangIndex + 1) % LANGUAGE_LIST.length])
    }, [i18n])

    return <button className={`button-outline button-tiny button-with-icon opacity-70 ${props.className}`} onClick={onLanguageButtonClick}>
                <LanguageIcon className="w-4 mr-1 opacity-70" />
                <span className="capitalize">{t("LANGUAGE_NAME")}</span>
            </button>
}
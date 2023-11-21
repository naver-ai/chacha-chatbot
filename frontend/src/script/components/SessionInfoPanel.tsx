import { LanguageIcon } from "@heroicons/react/20/solid"
import { useCallback, useMemo } from "react"
import { useTranslation } from "react-i18next"
import { LANGUAGE_LIST } from "src/i18n"
const format = require('string-format')

export const SessionInfoPanel = (props: {
    sessionId: string,
    name: string,
    age: number,
    children?: any
}) => {

    const [t] = useTranslation()

    const profile = useMemo(()=>format(t("SESSION_INFO.PROFILE_FORMAT"), {name: props.name, age: props.age}), [t, props.name, props.age])

    return <div className="container bg-slate-400/20 px-1.5 pr-1 py-1 flex items-center justify-between text-xs sm:text-sm sm:mt-2 sm:rounded-md border-collapse border-b-2 sm:border-none border-slate-300">
            <div>{t("SESSION_INFO.SESSION")}: {props.sessionId} ({profile})</div>
            {props.children}
            </div>
  }
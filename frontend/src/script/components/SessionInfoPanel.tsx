import { useMemo } from "react"
import { useTranslation } from "react-i18next"
const format = require('string-format')

export const SessionInfoPanel = (props: {
    sessionId: string,
    name: string,
    age: number,
    children?: any
}) => {

    const [t] = useTranslation()

    const profile = useMemo(()=>format(t("SESSION_INFO.PROFILE_FORMAT"), {name: props.name, age: props.age}), [t, props.name, props.age])

    return <div className="fixed left-0 right-0 top-0 z-[100] backdrop-blur-sm flex items-center justify-between text-sm shadow-md px-6 py-3 bg-white/50">
            <div className={"text-[12pt] font-extrabold"}>{t("TITLE")}</div>
            {false && <div>{t("SESSION_INFO.SESSION")}: {props.sessionId} ({profile})</div>}
            {props.children}
            </div>
  }
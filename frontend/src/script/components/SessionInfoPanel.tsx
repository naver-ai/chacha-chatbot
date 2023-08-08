export const SessionInfoPanel = (props: {
    sessionId: string,
    name: string,
    age: number,
    children?: any
}) => {
    return <div className="container bg-slate-400/20 px-1.5 pr-1 py-1 flex items-center justify-between text-xs sm:text-sm sm:mt-2 sm:rounded-md border-collapse border-b-2 sm:border-none border-slate-300">
            <div>세션: {props.sessionId} ({props.name}, {props.age}세)</div>
            {props.children}
            </div>
  }
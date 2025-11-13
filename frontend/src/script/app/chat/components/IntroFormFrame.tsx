export const IntroFormFrame = (props: {children?: any}) => {
    return <div className="flex flex-col justify-between h-screen intro-form-frame">
    <div className="my-auto mx-auto flex flex-col items-center gap-y-4">
        {props.children}
    </div>
    </div>
}
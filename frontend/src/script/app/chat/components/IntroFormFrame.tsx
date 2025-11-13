export const IntroFormFrame = (props: {children?: any}) => {
    return <div className="flex flex-col justify-between h-screen intro-form-frame">
    <div className="my-auto mx-auto flex flex-col items-center gap-y-4">
        <div className="text-xl font-black">어린이들을 위한 챗봇, 차차 (HCX)</div>
        {props.children}
    </div>
    </div>
}
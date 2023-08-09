export const IntroFormFrame = (props: {children?: any}) => {
    return <div className="flex flex-col justify-between h-screen intro-form-frame">
    <div className="my-auto mx-auto chachaContainer">
        <div className="chachaTextBox">
            <span>ChaCha</span>
        </div>
        <img src={require('../../../../CHACHA.png')}/>
    </div>
    {props.children}
    </div>
}
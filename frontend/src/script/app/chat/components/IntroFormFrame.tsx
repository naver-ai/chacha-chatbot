const vignetteUpperURL = new URL('../../../../vignette_upper.svg', import.meta.url).toString()
const vignetteLowerURL = new URL('../../../../vignette_under.svg', import.meta.url).toString()

export const IntroFormFrame = (props: {children?: any}) => {
    return <div className="flex flex-col justify-between h-screen intro-form-frame">
        <div className="my-auto mx-auto flex flex-col items-center gap-y-4">
            <img src={vignetteUpperURL} className="pointer-events-none absolute translate-y-[-180px] opacity-70" width={500}/>
            <img src={vignetteLowerURL} className="pointer-events-none absolute translate-y-[120px] opacity-70" width={500}/>
            <div className="text-xl font-black z-10">어린이들을 위한 챗봇, 차차 (HCX)</div>
            <div className="z-10">{props.children}</div>
        </div>
    </div>
}
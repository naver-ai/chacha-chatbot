export const BackgroundPanel = () => {
    return  <div className="background-panel fixed top-0 left-0 right-0 bottom-0 z-[-1] pointer-events-none">
        <img className={"absolute right-2 bottom-2"} src={require("../../powered_by_hcx.svg")} alt={"Powered by HyperCLOVA X"} width={120}/>
    </div>
}
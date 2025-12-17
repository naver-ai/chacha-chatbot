const poweredByHCXLogoURL = new URL('../../powered_by_hcx.svg', import.meta.url);
const nccLogoURL = new URL('../../ncc_logo.svg', import.meta.url);

export const BackgroundPanel = () => {

        return <>
            <div className="background-panel fixed top-0 left-0 right-0 bottom-0 z-[-1] pointer-events-none"/>
            <img className={"absolute right-8 bottom-4 hidden lg:block"} src={poweredByHCXLogoURL.href} alt={"Powered by HyperCLOVA X"} width={250}/>
            <img className={"absolute left-8 bottom-5 hidden lg:block"} src={nccLogoURL.href} alt={"NCC Logo"} width={150}/>
        </>
}
import React from 'react';

const MIN_TABLET_WIDTH = 768;

interface ContextValue {
    width: number;
    height: number;
}

interface ProviderValue extends ContextValue {
    isTablet: boolean;
}

const viewportContext = React.createContext<ContextValue | undefined>(undefined);

const ViewportProvider = ({ children }: { children: React.ReactElement }): React.ReactElement => {
    const [ width, setWidth ] = React.useState(window.innerWidth);
    const [ height, setHeight ] = React.useState(window.innerHeight);

    const handleWindowResize = () => {
        setWidth(window.innerWidth);
        setHeight(window.innerHeight);
    };

    React.useEffect(() => {
        window.addEventListener('resize', handleWindowResize);
        return () => window.removeEventListener('resize', handleWindowResize);
    }, []);

    return (
        <viewportContext.Provider value={{ width, height }}>
            {children}
        </viewportContext.Provider>
    );
};

const useViewport = (): ProviderValue => {
    const width = window.innerWidth;
    const height = window.innerHeight;
    return { width, height, isTablet: width >= MIN_TABLET_WIDTH };
};

export {
    ViewportProvider,
    useViewport
};

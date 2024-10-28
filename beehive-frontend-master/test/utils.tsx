import { ThemeProvider } from '@material-ui/core/styles';
import { configureStore, EnhancedStore } from '@reduxjs/toolkit';
import { render as rtlRender } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter as Router } from 'react-router-dom';

import { test as storeTest } from '../src/store';
import theme from '../src/theme';
import { ViewportProvider } from '../src/utils/viewport';

function render(
    ui,
    {
        preloadedState,
        store = configureStore({ ...storeTest.storeOptions, preloadedState }),
        ...renderOptions
    }: {
        preloadedState?: any,
        store?: EnhancedStore
    } = {}
) {
    function Wrapper({ children }) {
        // add all wrapper components that are added in App.tsx
        return (
            <Provider store={store}>
                <ThemeProvider theme={theme}>
                    <ViewportProvider>
                        <Router>
                            {children}
                        </Router>
                    </ViewportProvider>
                </ThemeProvider>
            </Provider>
        );
    }

    return rtlRender(ui, { wrapper: Wrapper, ...renderOptions });
}

// re-export everything
export * from '@testing-library/react';

// override render method
export {
    render
};

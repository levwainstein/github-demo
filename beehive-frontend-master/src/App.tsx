import { ThemeProvider } from '@material-ui/core/styles';
import React, { FunctionComponent, useEffect } from 'react';
import TagManager from 'react-gtm-module';
import { Provider } from 'react-redux';
import { BrowserRouter as Router, Redirect, Route, RouteProps, Switch } from 'react-router-dom';

import ActivateUser from './pages/ActivateUser';
import Dashboard from './pages/Dashboard';
import DashboardContributorHistory from './pages/DashboardContributorHistory';
import Error from './pages/Error';
import History from './pages/History';
import Login from './pages/Login';
import NewWork from './pages/NewWork';
import PrivacyPolicy from './pages/PrivacyPolicy';
import Rate from './pages/Rate';
import RedirectPage from './pages/RedirectPage';
import Register from './pages/Register';
import Registered from './pages/Registered';
import ResetPassword from './pages/ResetPassword';
import TermsOfUse from './pages/TermsOfUse';
import UserProfile from './pages/UserProfile';
import Work from './pages/Work';
import { signedIn } from './services/auth';
import store from './store';
import theme from './theme';
import { ViewportProvider } from './utils/viewport';

type AuthorizedRouteProps = RouteProps & {
    component: React.ComponentType<any>;
};

const AuthorizedRoute: FunctionComponent<AuthorizedRouteProps> = ({
    component,
    ...rest
}: AuthorizedRouteProps) => {
    return (
        <Route
            {...rest}
            render={() =>
                signedIn() ? React.createElement(component) : <Redirect to="/login" />
            }
        />
    );
};

const App: FunctionComponent = () => {

    useEffect(() => {
        const tagManagerArgs = {
            gtmId: `${process.env.REACT_APP_GTM_ID || 'GTM-5T27HGKK'}`
        };
        TagManager.initialize(tagManagerArgs);
    }, []);
    
    return (
        <Provider store={store}>
            <ThemeProvider theme={theme}>
                <ViewportProvider>
                    <Router>
                        <Switch>
                            <Route exact path="/login" component={Login} />
                            <Route exact path="/register" component={Register} />
                            <Route exact path="/register/success" component={Registered} />
                            <Route exact path="/register/activate" component={ActivateUser} />
                            <Route exact path="/reset/change" component={ResetPassword} />
                            <Route exact path="/terms-of-use" component={TermsOfUse} />
                            <Route exact path="/privacy-policy" component={PrivacyPolicy} />
                            <Route exact path="/profile" component={UserProfile} />
                            <Route exact path="/new-work" component={NewWork} />
                            
                            <AuthorizedRoute exact path="/" component={Work} />
                            <AuthorizedRoute exact path="/history" component={History} />
                            <AuthorizedRoute exact path="/dashboard" component={Dashboard} />
                            <AuthorizedRoute exact path="/dashboard/contributor-history" component={DashboardContributorHistory} />
                            <AuthorizedRoute exact path="/rate" component={Rate} />
                            <AuthorizedRoute exact path="/redirect" component={RedirectPage} />

                            <Route path="*" component={Error} />
                        </Switch>
                    </Router>
                </ViewportProvider>
            </ThemeProvider>
        </Provider>
    );
};

export default App;

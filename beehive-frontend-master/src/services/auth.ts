import manifest from '../../package.json';
import { refreshToken as apiRefreshToken, signIn as apiSignIn } from './api';
import { signOut as apiSignOut, signUp as apiSignUp } from './api';

const JWT_ADDITIONAL_CLAIM_PREFIX = 'bh-';

let refreshTokenId: NodeJS.Timeout | null = null;

// Register a new user into the system
export async function signUp(
    email: string, password: string, code: string, firstName?: string, lastName?: string,
    githubUser?: string, trelloUser?: string, upworkUser?: string, 
    availabilityWeeklyHours?: number, pricePerHour?: number
): Promise<any> {
    return apiSignUp(
        email, password, code, `frontend-${manifest.version}`, firstName, lastName,
        githubUser, trelloUser, upworkUser, availabilityWeeklyHours, pricePerHour
    );
}

// Parse the token claims
export function parseAccessTokenClaims(): any {
    const token = accessToken();

    if (!token) {
        return null;
    }

    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(
            c => {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }
        ).join(''));

        // token claims are now at the top level alongside all basic token
        // properties. we distinguish the user claims by their prefix
        const claims = JSON.parse(jsonPayload);
        return Object.keys(claims)
            .filter((k) => k.startsWith(JWT_ADDITIONAL_CLAIM_PREFIX))
            .reduce((obj, k) => {
                return Object.assign(obj, {
                    [k.substring(JWT_ADDITIONAL_CLAIM_PREFIX.length)]: claims[k]
                });
            }, {});
    } catch {
        return {};
    }
}

// Sign the user into the system
export async function signIn(email: string, password: string): Promise<any> {
    return apiSignIn(email, password)
        .then(response => {
            if (response.activated) {
                localStorage.setItem('access_token', response.accessToken);
                localStorage.setItem('refresh_token', response.refreshToken);

                // set refresh for expires in or a day if no expires in was provided
                setTokenRefresh(response.expiresIn || 24 * 60 * 60);

                return Promise.resolve({ activated: true });
            } else {
                return Promise.resolve({ activated: false, accessToken: response.accessToken });
            }
        });
}

// Sign the user out of the system
export async function signOut(): Promise<any> {
    if (refreshTokenId !== null) {
        clearInterval(refreshTokenId);
        refreshTokenId = null;
    }

    // we don't care if signout failed on the service
    return apiSignOut()
        .catch(() => null)
        .finally(() => {
            // remove tokens
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
        });
}

// Calling the refresh token API to refresh the access token
export async function refreshToken(): Promise<any> {
    console.log('Refreshing token');
    return apiRefreshToken()
        .then(response => {
            // replace access token
            localStorage.setItem('access_token', response.accessToken);

            // set refresh for expires in or a day if no expires in was provided
            setTokenRefresh(response.expiresIn || 24 * 60 * 60);

            console.log('Token refresh successful');

            return Promise.resolve();
        })
        .catch(error => {
            console.log(`Error refreshing token: ${JSON.stringify(error)}`);
            return signOut().then(() => {
                window.location.replace('/login');
            });
        });
}

// Gets the current access token
export function accessToken(): string | null {
    return localStorage.getItem('access_token');
}

// Checks if the user is signed in
export function signedIn(): boolean {
    return !!localStorage.getItem('access_token');
}

// Setting a timer to refresh the access token
function setTokenRefresh(expiresInSeconds: number): void {
    if (refreshTokenId !== null) {
        clearInterval(refreshTokenId);
        refreshTokenId = null;
    }

    // refresh after 95% of token valid time has passed so we have a working one
    const refreshInSeconds = Math.round(expiresInSeconds * 0.95);
    refreshTokenId = setInterval(refreshToken, refreshInSeconds * 1000);
}

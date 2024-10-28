import { render, screen } from '../../../../test/utils';
import NavBar from './navBar';

jest.mock('../../../services/auth');

describe('NavBar', () => {
    it('renders without logged in user', () => {
        render(
            <NavBar
                signedIn={false}
                isAdmin={false}
                onSignOut={() => null}
                onOpenHotkeysDialog={() => null}
            />
        );

        expect(screen.queryByTestId('logo-image')).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'help' })).not.toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'admin-dashboard' })).not.toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'help' })).not.toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'my-account' })).not.toBeInTheDocument();
        expect(screen.queryByText('Settings')).not.toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'History' })).not.toBeInTheDocument();
        expect(screen.queryByText('Sign out')).not.toBeInTheDocument();
    });

    it('renders with logged in user', () => {
        render(
            <NavBar
                signedIn={true}
                isAdmin={false}
                onSignOut={() => null}
                onOpenHotkeysDialog={() => null}
            />
        );

        expect(screen.queryByTestId('logo-image')).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'help' })).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'admin-dashboard' })).not.toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'help' })).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'my-account' })).toBeInTheDocument();
        expect(screen.queryByText('Settings')).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'History' })).toBeInTheDocument();
        expect(screen.queryByText('Sign out')).toBeInTheDocument();
    });

    it('renders with logged in administrator user', () => {
        render(
            <NavBar
                signedIn={true}
                isAdmin={true}
                onSignOut={() => null}
                onOpenHotkeysDialog={() => null}
            />
        );

        expect(screen.queryByTestId('logo-image')).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'help' })).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'admin-dashboard' })).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'help' })).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'my-account' })).toBeInTheDocument();
        expect(screen.queryByText('Settings')).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'History' })).toBeInTheDocument();
        expect(screen.queryByText('Sign out')).toBeInTheDocument();
    });
});

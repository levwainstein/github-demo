describe('test register and login', () => {
    it('login with no or wrong credentials does not work', () => {
        cy.visit('http://localhost:15000');

        // should have been navigated to '/login'
        cy.url().should('include', '/login');

        // submit button should be there
        cy.get('button[type=submit]').should('be.visible');

        // submit with no input shows error
        cy.get('button[type=submit]').click();
        cy.get('.Mui-error').should('be.visible');
        cy.get('.Mui-error').contains('Required');
        cy.get('.Mui-error').parent().contains('E-mail');

        // type invalid email
        cy.get('input[type=email]').type('nope');
        cy.get('.Mui-error').should('be.visible');
        cy.get('.Mui-error').contains('Invalid email address');
        cy.get('.Mui-error').parent().contains('E-mail');

        // valid email, no password
        cy.get('input[type=email]').type('nope@nope.nope');
        cy.get('.Mui-error').should('be.visible');
        cy.get('.Mui-error').contains('Required');
        cy.get('.Mui-error').parent().contains('Password');

        // valid email and password
        cy.get('input[type=password]').type('123');
        cy.get('.Mui-error').should('not.exist');

        // try to login with wrong credentials
        cy.get('button[type=submit]').click();
        cy.get('form').contains('Wrong credentials');
    });

    it('registration without invite code does not work', () => {
        cy.visit('http://localhost:15000/register');

        // submit button should be there
        cy.get('button[type=submit]').should('be.visible');

        // generate user email for registration
        const userEmail = `test${Date.now()}@beehivesoftware.com`;

        cy.get('input[type=email]').type(userEmail);
        cy.get('input[type=password][name=password]').type('1234');
        cy.get('input[type=password][name=password2]').type('1234').blur();

        cy.get('[type="checkbox"]').check();
        cy.get('button[type=submit]').click();

        // error should be displayed
        cy.get('form').contains('Registration is currently not public');
    });

    it('registration with bad invite code does not work', () => {
        cy.visit('http://localhost:15000/register#nope');

        // submit button should be there
        cy.get('button[type=submit]').should('be.visible');

        // generate user email for registration
        const userEmail = `test${Date.now()}@beehivesoftware.com`;

        cy.get('input[type=email]').type(userEmail);
        cy.get('input[type=password][name=password]').type('1234');
        cy.get('input[type=password][name=password2]').type('1234').blur();
        cy.get('[type="checkbox"]').check();
        cy.get('button[type=submit]').click();

        // error should be displayed
        cy.get('form').contains('Registration is currently not public');
    });

    it('registration with valid invite code and login with correct credentials do work', () => {
        cy.visit('http://localhost:15000/register#fake-registration-code');

        // submit button should be there
        cy.get('button[type=submit]').should('be.visible');

        // generate user email for registration
        const userEmail = `test${Date.now()}@beehivesoftware.com`;

        cy.get('input[type=email]').type(userEmail);
        cy.get('input[type=password][name=password]').type('1234');
        cy.get('input[type=password][name=password2]').type('1234').blur();
        cy.get('[type="checkbox"]').check();
        cy.get('button[type=submit]').click();

        // should have been navigated to '/register/success'
        cy.url().should('equal', 'http://localhost:15000/register/success');

        // my account button should not be visible since the account is not confirmed yet
        cy.get('button[aria-label="my-account"]').should('not.exist');

        // navigating to any page should redirect to login
        cy.visit('http://localhost:15000/history');

        // should have been navigated to '/login'
        cy.url().should('include', '/login');

        // use registered credentials to log in
        cy.get('input[type=email]').type(userEmail);
        cy.get('input[type=password]').type('1234');
        cy.get('button[type=submit]').click();

        // should have been navigated to '/register/success' again since the account is not confirmed
        cy.url().should('equal', 'http://localhost:15000/register/success');

        // my account button should still not be visible
        cy.get('button[aria-label="my-account"]').should('not.exist');

        // navigating to any page should again redirect to login
        cy.visit('http://localhost:15000/history');

        // should have been navigated to '/login'
        cy.url().should('include', '/login');

        // go to activate account with no code
        cy.visit('http://localhost:15000/register/activate');

        // error should be displayed
        cy.get('h1').contains('Account Activation Failed');

        // go to activate account with bad code
        cy.visit('http://localhost:15000/register/activate?c=1234');

        // error should be displayed
        cy.get('h1').contains('Account Activation Failed');

        // activate account with correct code
        //const activationCode = getActivationCode(userEmail);
        cy.task(
            'queryTestDb',
            {
                query: 'SELECT `activation_token` FROM `user` WHERE `email` = ?',
                args: [ userEmail ]
            }
        ).then((activationResult) => {
            cy.visit(
                `http://localhost:15000/register/activate?c=${activationResult[0].activation_token}`
            );

            // success title
            cy.get('h1').contains('Your Account Has Been Activated!');

            // navigating to any page should still redirect to login
            cy.visit('http://localhost:15000/history');

            // should have been navigated to '/login'
            cy.url().should('include', '/login');

            // use registered credentials to log in
            cy.get('input[type=email]').type(userEmail);
            cy.get('input[type=password]').type('1234');
            cy.get('button[type=submit]').click();

            // should have been navigated to '/'
            cy.url().should('equal', 'http://localhost:15000/');

            // my account button should be visible again
            cy.get('button[aria-label="my-account"]').should('be.visible');
        });
    });
});

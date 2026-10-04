/**
 * E2E Test — Full flow: Sign Up → Log In → Create Post → Verify Post.
 *
 * Uses data-testid selectors added to MUI components for resilient targeting.
 * Each run generates a unique user via Date.now() to avoid DB conflicts.
 */

describe('Authentication & Post Flow', () => {
  const uniqueId = Date.now();
  const testUser = {
    name: `E2E User ${uniqueId}`,
    email: `e2e_test_${uniqueId}@example.com`,
    password: 'password123',
  };
  const testPost = {
    title: `Test Post ${uniqueId}`,
    body: `This is an automated E2E test post created at ${uniqueId}`,
  };

  it('should sign up, log in, create a post, and verify it appears in the feed', () => {
    // ---------------------------------------------------------------
    // Step 1: Sign Up
    // ---------------------------------------------------------------

    // Arrange
    cy.intercept('POST', '/api/signup').as('signupRequest');
    cy.visit('/signup');

    // Act
    cy.get('[data-testid="signup-name"]').type(testUser.name);
    cy.get('[data-testid="signup-email"]').type(testUser.email);
    cy.get('[data-testid="signup-password"]').type(testUser.password);
    cy.get('[data-testid="signup-confirm-password"]').type(testUser.password);
    cy.get('[data-testid="signup-submit"]').click();

    // Assert — wait for the API call, then verify redirect to home
    cy.wait('@signupRequest').its('response.statusCode').should('eq', 201);
    cy.url().should('eq', Cypress.config().baseUrl + '/');

    // ---------------------------------------------------------------
    // Step 2: Log Out (so we can test the login flow next)
    // ---------------------------------------------------------------

    // Arrange — properly log out via the server API to clear both
    // the server session and the browser cookie
    cy.request('POST', '/api/logout');

    // ---------------------------------------------------------------
    // Step 3: Log In
    // ---------------------------------------------------------------

    // Arrange
    cy.intercept('POST', '/api/login').as('loginRequest');
    cy.visit('/login');

    // Act
    cy.get('[data-testid="login-email"]').type(testUser.email);
    cy.get('[data-testid="login-password"]').type(testUser.password);
    cy.get('[data-testid="login-submit"]').click();

    // Assert — wait for the API call, then verify redirect to home
    cy.wait('@loginRequest').its('response.statusCode').should('eq', 200);
    cy.url().should('eq', Cypress.config().baseUrl + '/');

    // ---------------------------------------------------------------
    // Step 4: Create a Post
    // ---------------------------------------------------------------

    // Arrange
    cy.intercept('POST', '/api/posts').as('createPostRequest');
    cy.visit('/new-post');

    // Act
    cy.get('[data-testid="post-input"]').type(testPost.title);
    // Tiptap: type into the editable element inside the editor wrapper
    cy.get('[data-testid="post-body"] [contenteditable="true"]').type(testPost.body);
    cy.get('[data-testid="post-submit"]').click();

    // Assert — wait for the API call, then verify redirect and post visibility.
    // Search by text (not .first()): agent bots may have posted in the meantime.
    cy.wait('@createPostRequest').its('response.statusCode').should('eq', 201);
    cy.url().should('eq', Cypress.config().baseUrl + '/');
    cy.contains('[data-testid="post-content"]', testPost.body).should('be.visible');
  });
});
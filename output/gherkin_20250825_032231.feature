Feature: Google Login - New User Signup

  Scenario: Successful signup with Google account
    When The user clicks the "Sign in with Google" button
    And The user grants Hackwave-webApp access to their Google account (email, name, profile picture)
    Then The user is redirected to the Hackwave-webApp dashboard
    And A new Hackwave-webApp account is created for the user
    And The user's email, name, and profile picture (if available) are populated in their Hackwave-webApp profile
    And A session is established for the user

  Scenario: User cancels Google account access
    When The user clicks the "Sign in with Google" button
    And The user denies Hackwave-webApp access to their Google account
    Then The user is redirected back to the signup page
    And An error message is displayed: "Google account access was denied. Please try again or use another signup method."

  Scenario: Google account already exists with a Hackwave-webApp account
    Given A Hackwave-webApp account already exists with the same email address as the Google account
    When The user clicks the "Sign in with Google" button
    And The user grants Hackwave-webApp access to their Google account
    Then The user is redirected to the Hackwave-webApp dashboard
    And The user is logged in to the existing Hackwave-webApp account
    And The Google account is linked to the existing Hackwave-webApp account
    And A success message is displayed: "Your Google account has been successfully linked to your existing Hackwave-webApp account."

  Scenario: Google API returns an error
    Given The Google API is temporarily unavailable
    When The user clicks the "Sign in with Google" button
    Then The user is redirected back to the signup page
    And An error message is displayed: "There was an error communicating with Google. Please try again later."
    And The error is logged for debugging purposes

  Scenario: Google returns incomplete user data (missing email)
    When The user clicks the "Sign in with Google" button
    And The user grants Hackwave-webApp access to their Google account
    And Google does not return the user's email address
    Then The user is redirected back to the signup page
    And An error message is displayed: "Unable to retrieve your email address from Google. Please try again or use another signup method."

  Scenario: Google returns invalid user data (invalid email format)
    When The user clicks the "Sign in with Google" button
    And The user grants Hackwave-webApp access to their Google account
    And Google returns an invalid email address format
    Then The user is redirected back to the signup page
    And An error message is displayed: "The email address provided by Google is invalid. Please try again or use another signup method."

Feature: Google Login - Existing User Login

  Scenario: Google Login button is not accessible
    When The user uses a screen reader to navigate the signup page
    Then The screen reader announces the "Sign in with Google" button with a descriptive label
    And The user can activate the button using keyboard navigation
    Given The user is on the login page

  Scenario: Successful login with Google account
    Given The user has previously linked their Hackwave-webApp account to their Google account
    When The user clicks the "Sign in with Google" button
    And The user grants Hackwave-webApp access to their Google account
    Then The user is redirected to the Hackwave-webApp dashboard
    And The user is logged in to their Hackwave-webApp account
    And A session is established for the user

  Scenario: User cancels Google account access during login
    Given The user has previously linked their Hackwave-webApp account to their Google account
    When The user clicks the "Sign in with Google" button
    And The user denies Hackwave-webApp access to their Google account
    Then The user is redirected back to the login page
    And An error message is displayed: "Google account access was denied. Please try again or use another login method."

  Scenario: Google account not linked to any Hackwave-webApp account
    When The user clicks the "Sign in with Google" button
    And The user grants Hackwave-webApp access to their Google account
    And No Hackwave-webApp account is associated with the Google account's email address
    Then The user is redirected to a page prompting them to create a new Hackwave-webApp account or link their existing account
    And A message is displayed: "This Google account is not linked to any Hackwave-webApp account. Would you like to create a new account or link it to an existing one?"

  Scenario: Google API returns an error during login
    Given The user has previously linked their Hackwave-webApp account to their Google account
    Given The Google API is temporarily unavailable
    When The user clicks the "Sign in with Google" button
    Then The user is redirected back to the login page
    And An error message is displayed: "There was an error communicating with Google. Please try again later."
    And The error is logged for debugging purposes

Feature: Google Login - Account Linking

  Scenario: Google Login button is not accessible on login page
    When The user uses a screen reader to navigate the login page
    Then The screen reader announces the "Sign in with Google" button with a descriptive label
    And The user can activate the button using keyboard navigation
    Given The user is logged in to their Hackwave-webApp account

  Scenario: Successful account linking
    Given The user navigates to the account settings page
    When The user clicks the "Link Google Account" button
    And The user grants Hackwave-webApp access to their Google account
    Then The user's Hackwave-webApp account is linked to their Google account
    And A success message is displayed: "Your Google account has been successfully linked."

  Scenario: User cancels Google account access during account linking
    Given The user navigates to the account settings page
    When The user clicks the "Link Google Account" button
    And The user denies Hackwave-webApp access to their Google account
    Then The user remains on the account settings page
    And An error message is displayed: "Google account access was denied. Account linking was not completed."

  Scenario: Google account already linked to another Hackwave-webApp account
    Given The user navigates to the account settings page
    Given Another Hackwave-webApp account is already linked to the user's Google account
    When The user clicks the "Link Google Account" button
    And The user grants Hackwave-webApp access to their Google account
    Then An error message is displayed: "This Google account is already linked to another Hackwave-webApp account. Please unlink it from the other account first."

  Scenario: Successful account unlinking
    Given The user's Hackwave-webApp account is linked to their Google account
    Given The user navigates to the account settings page
    When The user clicks the "Unlink Google Account" button
    And The user confirms the unlinking action
    Then The user's Hackwave-webApp account is no longer linked to their Google account
    And A success message is displayed: "Your Google account has been successfully unlinked."

Feature: Google Login - Error Handling and Fallback

  Scenario: Account unlinking is cancelled
    Given The user's Hackwave-webApp account is linked to their Google account
    Given The user navigates to the account settings page
    When The user clicks the "Unlink Google Account" button
    And The user cancels the unlinking action
    Then The user's Hackwave-webApp account remains linked to their Google account
    And No message is displayed

  Scenario: Network error during Google Login
    Given The user attempts to log in with Google
    When There is a network error preventing communication with Google
    Then An error message is displayed: "A network error occurred. Please check your internet connection and try again."
    And The user is offered the option to log in using their username and password

  Scenario: Invalid credentials returned by Google
    Given The user attempts to log in with Google
    When Google returns invalid credentials
    Then An error message is displayed: "Invalid Google credentials. Please check your Google account and try again."
    And The user is offered the option to log in using their username and password

  Scenario: Google outage - Fallback authentication
    Given The Google authentication service is unavailable
    When The user attempts to log in with Google
    Then An error message is displayed: "Google Login is currently unavailable. Please try again later or use your username and password to log in."
    And The username/password login form is prominently displayed

Feature: Google Login - Admin Dashboard

  Scenario: Rate limiting by Google API
    Given The application exceeds the Google API rate limit
    When The user attempts to log in with Google
    Then An error message is displayed: "Google Login is temporarily unavailable due to high traffic. Please try again later."
    And The application implements a retry mechanism with exponential backoff

  Scenario: Track Google Login signups
    Given The administrator is logged into the admin dashboard
    When The administrator views the user statistics
    Then The number of signups via Google Login is displayed

  Scenario: Track Google Login logins
    Given The administrator is logged into the admin dashboard
    When The administrator views the user statistics
    Then The number of logins via Google Login is displayed

Feature: Google Login - Data Privacy and Consent

  Scenario: Track Google Login usage over time
    Given The administrator is logged into the admin dashboard
    When The administrator views the Google Login usage report
    Then A graph showing the number of Google Login signups and logins over time is displayed

  Scenario: User is informed about data access
    Given The user is about to sign up or link their account with Google
    When The user clicks the "Sign in with Google" button
    Then A consent screen is displayed showing the data Hackwave-webApp will access (email, name, profile picture)
    And The user is given the option to grant or deny access

Feature: Google Login - Accessibility

  Scenario: User revokes Google Login access
    Given The user has granted Hackwave-webApp access to their Google account
    When The user revokes Hackwave-webApp's access to their Google account through their Google account settings
    Then The next time the user attempts to log in with Google, they are prompted to grant access again
    And The user's Hackwave-webApp account remains active but requires a different login method

  Scenario: Google Login button has proper ARIA attributes
    Given The user is on the signup or login page
    When The user inspects the "Sign in with Google" button in the browser's developer tools
    Then The button has appropriate ARIA attributes for accessibility (e.g., aria-label, role)

  Scenario: Google Login flow is keyboard accessible
    Given The user is on the signup or login page
    When The user navigates through the page using the keyboard (Tab key)
    Then The user can focus on the "Sign in with Google" button
    And The user can activate the button using the Enter or Space key
    And The Google consent screen is also keyboard accessible

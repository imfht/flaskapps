// Login.html testing
describe('Testing User Sign Up, Login and Logout, Forgot password', function() {


  it('Sign Up', function() {
      browser.get('http://localhost:5000/');
      //Click on the SignUp Link
      element(by.id('signUp')).click();
      // Fill in the fields
      element(by.model('name')).sendKeys("Leo G");
      element(by.model("email")).sendKeys("root@localhost");
      element(by.model('password')).sendKeys("Str0ng P@$$w)*&^+=");


      element(by.css(".btn")).click()
          .then(function(){
              var EC = protractor.ExpectedConditions;
              var toastMessage = $('.toast-message');
              browser.wait(EC.visibilityOf(toastMessage), 60) //wait until toast is displayed
                  .then(function(){
                      expect(toastMessage.getText()).toBe("User created successfully");

    });
  });

    });


    it(' Test Forgot password and Login', function() {
        browser.get('http://localhost:5000/');
        //Click on the Forgot password Link

        element(by.id('forgotPassword')).click();
        // Fill in the fields

        element(by.id("iEmail")).sendKeys("root@localhost");

        element(by.id("fpass")).click()
            .then(function(){
                var EC = protractor.ExpectedConditions;
                var toastMessage = $('.toast-message');
                browser.wait(EC.visibilityOf(toastMessage), 60) //wait until toast is displayed
                    .then(function(){
                        expect(toastMessage.getText()).toBe("Password reset email has been sent successfully");

                                    });
                         });





                 //Test LogIn
        element(by.id('logIn')).click();
        // Fill in the fields

       element(by.id("inEmail")).clear();
       element(by.id("inEmail")).sendKeys("root@localhost");
       element(by.id("inPassword")).clear();
       element(by.id("inPassword")).sendKeys("Str0ng P@$$w)*&^+=");
       element(by.id("signButton")).click()
           .then(function() {

                        expect(browser.getTitle()).toEqual('Home | Flask-Scaffold');

                });

          });

});

//Roles CRUD Tests
describe('Roles/Users CRUD tests ', function() {
  // Page Object https://angular.github.io/protractor/#/page-objects
    var Role = function() {
                   var nameInput = element(by.id("name"));
                   this.get = function() {
                                   browser.get('http://localhost:5000/');



                                       };
                   this.setName = function(name) {
                                        nameInput.clear();
                                        nameInput.sendKeys(name);
                                      };
                    this.toast = function(message){
                                        $('.btn.btn-primary').click()  // css selectors http://angular.github.io/protractor/#/api?view=build$
                                            .then(function() {
                                                  var EC = protractor.ExpectedConditions;
                                                  var toastMessage = $('.toast-message');
                                                  browser.wait(EC.visibilityOf(toastMessage), 6000) //wait until toast is displayed
                                                             .then(function(){
                                                                    expect(toastMessage.getText()).toBe(message);

                                                                        });
                                                                  });
                                    }
                    };



    it('Should add a new Role', function() {
        var role = new Role();
        //Get Roles URL
        role.get();
        // Goto the new menu
        element(by.linkText('Roles')).click();
        element(by.linkText('New')).click();
        // Fill in the fields
        role.setName("suppport");
        // Expectations
        role.toast("Role saved successfully");

        });

    it('Should  edit a Role', function() {

        var role = new Role();
        // Goto the edit menu
         element(by.linkText('Roles')).click();
          element(by.id('editButton')).click();
        // Fill in the fields
        role.setName("admin");
        // Expectations
        role.toast("Update was a success");

    });


//Users

var User = function() {

    var name = element(by.id('name'));
    var email = element(by.id("email"));
    var password =  element(by.id('password'));

    this.get = function() {
                               browser.get('http://localhost:5000/');
                                   };
    this.setName = function(nameText) { name.clear(); name.sendKeys(nameText); };
    this.setEmail = function(emailText) { email.clear(); email.sendKeys(emailText); };
    this.setPassword = function(passwordText) { password.clear(); password.sendKeys(passwordText); };
    // radio button
    this.setActive = function(activeText) {  element(by.css("input[type='radio'][value={0}".format({activeText}))).click(); };

    // drop down
    this.setRole = function() {  element(by.cssContainingText('option', 'admin')).click(); };


    this.toast = function(message){
                                      $('.btn.btn-primary').click()  // css selectors http://angular.github.io/protractor/#/api?view=build$
                                        .then(function() {
                                              var EC = protractor.ExpectedConditions;
                                              var toastMessage = $('.toast-message');
                                              browser.wait(EC.visibilityOf(toastMessage), 6000) //wait until toast is displayed
                                                         .then(function(){
                                                                expect(toastMessage.getText()).toBe(message);

                                                                    });
                                                              });
                                }
                };


                it('Should add a new User', function() {

                    var user = new User();

                    // Get users URL
                    user.get();

                    // Goto the new menu
                    element(by.linkText('Users')).click();
                    element(by.linkText('New')).click();

                    // Fill in the Fields

                        user.setEmail("leo@techarena51.com");
                        user.setPassword("Your Title text here");
                        user.setName("Your Title text here");
                        element(by.css("input[type='radio'][value='0']")).click();
                        user.setRole();

                    //Expectations
                    user.toast("User saved successfully");

                  });

                it('Should  edit a User', function() {

                    var user = new User();

                    user.get();

                    //Goto the edit menu
                    element(by.linkText('Users')).click();
                     element(by.id('editButton')).click();

                    // Fill in the fields

                        user.setEmail("leo@leog.in");
                        user.setPassword("Your Updated Title text here");
                        user.setName("Your Updated Title text here");
                        element(by.css("input[type='radio'][value='1']")).click();
                        user.setRole();

                    //Expectations
                    user.toast("Update was a success");



                });

                it('Should  delete a User', function() {
                    browser.get('http://localhost:5000/');
                    element(by.linkText('Users')).click();
                    element(by.id('deleteButton')).click()
                    .then(function(){
                        var EC = protractor.ExpectedConditions;
                        var toastMessage = $('.toast-message');
                         browser.wait(EC.visibilityOf(toastMessage), 60) //wait until toast is displayed
                            .then(function(){

                                expect(toastMessage.getText()).toBe("User deleted successfully")

                      });

                  });
                });


// Users End

     it('Should  delete a Role', function() {
        role = new Role();
      element(by.linkText('Roles')).click();
        element(by.id('deleteButton')).click()
            .then(function(){
                var EC = protractor.ExpectedConditions;
                var toastMessage = $('.toast-message');
                 browser.wait(EC.visibilityOf(toastMessage), 60) //wait until toast is displayed
                    .then(function(){

                        expect(toastMessage.getText()).toBe("Role deleted successfully")

              });

                          });
        });

});

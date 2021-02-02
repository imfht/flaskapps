exports.config = {{
  framework: 'jasmine',
  seleniumAddress: 'http://localhost:4444/wd/hub',
  specs: ['spec.js'],

  onPrepare: function() {{

       browser.get('http://localhost:5000/');
       element(by.id('signUp')).click();
       // Fill in the fields
       element(by.model('name')).sendKeys("Leo G");
       element(by.model("email")).sendKeys("root@localhost");
       element(by.model('password')).sendKeys("Str0ng P@$$w)*&^+=");


       element(by.css(".btn")).click()
           .then(function(){{
               var EC = protractor.ExpectedConditions;
               var toastMessage = $('.toast-message');
               browser.wait(EC.visibilityOf(toastMessage), 60) //wait until toast is displayed
                   .then(function(){{
                       expect(toastMessage.getText()).toBe("User created successfully");

     }});
   }});

  element(by.id('logIn')).click();
  element(by.id("inEmail")).clear();
  element(by.id("inEmail")).sendKeys("root@localhost");
  element(by.id("inPassword")).clear();
  element(by.id("inPassword")).sendKeys("Str0ng P@$$w)*&^+=");
  element(by.id("signButton")).click()
           .then(function() {{


                  expect(browser.getTitle()).toEqual('Home | Flask-Scaffold');

                }});



  }}
}}

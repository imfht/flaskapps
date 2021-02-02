// spec.js
describe('Testing {Resources} CRUD Module', function() {{

var {Resource} = function() {{
        {protractor_page_objects}

        this.get = function() {{
                                   browser.get('http://localhost:5000/');
                                       }};

        this.toast = function(message){{
                                        $('.btn.btn-primary').click()  // css selectors http://angular.github.io/protractor/#/api?view=build$
                                            .then(function() {{
                                                  var EC = protractor.ExpectedConditions;
                                                  var toastMessage = $('.toast-message');
                                                  browser.wait(EC.visibilityOf(toastMessage), 6000) //wait until toast is displayed
                                                             .then(function(){{
                                                                    expect(toastMessage.getText()).toBe(message);

                                                                        }});
                                                                  }});
                                    }}
                    }};

it('Should add a new {Resource}', function() {{

    var {resource} = new {Resource}();

    // Get {resources} URL
    {resource}.get();

    // Goto the new menu
    element(by.linkText('{Resources}')).click();
    element(by.linkText('New')).click();

    // Fill in the Fields
    {protractor_add_elments}

    //Expectations
    {resource}.toast("{Resource} saved successfully");

  }});

it('Should  edit a {Resource}', function() {{

    var {resource} = new {Resource}();

    {resource}.get();

    //Goto the edit menu
    element(by.linkText('{Resources}')).click();
     element(by.id('editButton')).click();

    // Fill in the fields
    {protractor_edit_elments}

    //Expectations
    {resource}.toast("Update was a success");



}});

it('Should  delete a {Resource}', function() {{
    browser.get('http://localhost:5000/');
    element(by.linkText('{Resources}')).click();
    element(by.id('deleteButton')).click()

    .then(function(){{

        var EC = protractor.ExpectedConditions;
        var toastMessage = $('.toast-message');

         browser.wait(EC.visibilityOf(toastMessage), 60) //wait until toast is displayed
            .then(function(){{

                expect(toastMessage.getText()).toBe("{Resource} deleted successfully")

      }});

  }});
}});

  }});

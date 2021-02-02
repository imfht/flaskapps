exports.config = {
  framework: 'jasmine',
  seleniumAddress: 'http://localhost:4444/wd/hub',
  specs: [  
   'app/templates/users/spec.js'   
    
   //Specs
   , 'app/templates/alarms/spec.js' 

  ]
}


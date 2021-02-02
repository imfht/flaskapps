angular.module('myApp', ['ui.router', 'ngResource',  'datatables' , 'myApp.controllers', 'myApp.services',
                         'satellizer','toaster', 'ngAnimate', 'angular-google-analytics',
                              'datatables.bootstrap']);

angular.module('myApp')
  .run( function($rootScope, $state){
                //$rootScope.$on('$stateChangeStart'
                $rootScope.$state = $state;
                $rootScope.$state.current.title = "Flask-Scaffold";
                }
    );

angular.module('myApp').config(function( $stateProvider , $urlRouterProvider, $authProvider, AnalyticsProvider) {

   // Google Analytics
    AnalyticsProvider.setAccount('UA-37519052-11');
    AnalyticsProvider.setDomainName('seven.leog.in');

   // Satellizer configuration that specifies which API
  // route the JWT should be retrieved from
    $authProvider.loginUrl = '/api/v1/login.json';
    $urlRouterProvider.otherwise('/login')

 //If a user is already logged in, the Login window if requested need not be displayed.
   function skipIfLoggedIn($q, $auth, $state) {
      var deferred = $q.defer();
      if ($auth.isAuthenticated()) {

        //deferred.reject();
        $state.go('home');

      } else {
        deferred.resolve();
      }
      return deferred.promise;
    }

   //Redirect unauthenticated users to the login state
   function loginRequired($q, $location, $auth, $state) {
      var deferred = $q.defer();
      if ($auth.isAuthenticated()) {
        deferred.resolve();
      } else {
        $location.href='/login';
      }
      return deferred.promise;
    }

$stateProvider.state('login', {
	url: '/login',
	templateUrl: 'login.html',
	controller: 'LoginController',
    title: 'Sign In',
    resolve: {
          skipIfLoggedIn: skipIfLoggedIn
        }

  }).state('ForgotPassword', {
	url: '/forgotpassword/:token',
	templateUrl: 'forgotpassword.html',
	controller: 'LoginController',
    resolve: {
          skipIfLoggedIn: skipIfLoggedIn
        }

  }).state('home', {
    url: '/',
    templateUrl: 'home.html',
    title: 'Home',
    resolve: {
          loginRequired: loginRequired
        }

  })

  // Routes for roles


  .state('roles', {
        // Note: abstract state cannot be loaded, but it still needs a ui-view for its children to populate.
        // https://github.com/angular-ui/ui-router/wiki/Nested-States-and-Nested-Views
        abstract: true,
        url: '/roles',
        title: 'Roles',
        template: '<ui-view/>'
    })

  .state('roles.list', {
    url: '/list',
    templateUrl: 'roles/index.html',
    controller: 'RoleListController',
    resolve: {
          loginRequired: loginRequired
        }


  }).state('roles.new', {
    url: '/new',
    templateUrl: '/roles/add.html',
    controller: 'RoleCreateController',
    resolve: {
          loginRequired: loginRequired
        }

    }).state('roles.edit', {
    url: '/:id/edit',
    templateUrl: 'roles/update.html',
    controller: 'RoleEditController',
    resolve: {
          loginRequired: loginRequired
        }

        })

        // End Routes for roles
  // Routes for users

   .state('users', {
        // Note: abstract state cannot be loaded, but it still needs a ui-view for its children to populate.
        // https://github.com/angular-ui/ui-router/wiki/Nested-States-and-Nested-Views
        abstract: true,
        url: '/users',
        title: 'Users',
        template: '<ui-view/>'
    })
  .state('users.list', {
    url: '/list',
    templateUrl: 'users/index.html',
    controller: 'UserListController',
    title: 'Users',
    resolve: {
          loginRequired: loginRequired
        }


  }).state('users.new', {
    url: '/new',
    templateUrl: '/users/add.html',
    controller: 'UserCreateController',

    resolve: {
          loginRequired: loginRequired
        }

    }).state('users.edit', {
    url: '/:id/edit',
    templateUrl: 'users/update.html',
    controller: 'UserEditController',
    resolve: {
          loginRequired: loginRequired
        }

        })

    // End Routes for users
   
   
   // States
   


  ;

  })
  .directive('stringToNumber', function() {
  return {
    require: 'ngModel',
    link: function(scope, element, attrs, ngModel) {
      ngModel.$parsers.push(function(value) {
        return '' + value;
      });
      ngModel.$formatters.push(function(value) {
        return parseFloat(value, 10);
      })
       }
  };
})
.directive('formatdate', function () {
  return {
    restrict: 'A',
    require: 'ngModel',
    link: function (scope, element, attrs, ngModel) {

      //format text going to user (model to view)
      ngModel.$formatters.push(function(date) {
        return new Date(date);
      });

      //format text from the user (view to model)
     // ngModel.$parsers.push(function(value) {
      //  return value.toLowerCase();
     // });
    }
  }
}).controller('LogoutCtrl', function($auth, $state, $window, toaster, $scope) { // Logout the user if they are authenticated.

  //Display the Logout button for authenticated users only
  $scope.isAuthenticated = function() {
      return $auth.isAuthenticated();
    };

    $scope.logout = function(){

     if (!$auth.isAuthenticated()) { return; }
     $auth.logout()
      .then(function() {

        toaster.pop({
                type: 'success',
                body: 'Logging out',
                showCloseButton: true,

                });

        $state.go('login');

      });
      }


});


angular.module('myApp.services', []);
angular.module('myApp.controllers', []);

angular.module('myApp').run(function(Analytics) {
            Analytics.pageView();
 });

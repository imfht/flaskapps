import { UserEditModule } from './user-edit.module';

describe('EditModule', () => {
  let editModule: UserEditModule;

  beforeEach(() => {
    editModule = new UserEditModule();
  });

  it('should create an instance', () => {
    expect(editModule).toBeTruthy();
  });
});

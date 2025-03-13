// source: https://stackoverflow.com/questions/79446532/onesignal-login-function-creates-a-seperate-user-record
export async function registerOneSignal(userId) {
  // Initialize OneSignal and request notification permission
  OneSignalDeferred.push(async function (OneSignal) {
    if (!OneSignal.initialized) {
      await OneSignal.init({
        appId: 'dc6f6c0b-b679-4c19-9db3-021e0cf7a297',
      })
    }
    if (userId) {
      console.log('Logging in with ID:', userId)
      await OneSignal.login(userId.toString()).catch((error) => {
        console.error('OneSignal login error:', error)
      })
    }
    OneSignal.Notifications.requestPermission()
  })
}

export async function logoutOneSignal() {
  OneSignalDeferred.push(async function (OneSignal) {
    await OneSignal.logout()
  })
  console.log('Logged out of OneSignal.')
}

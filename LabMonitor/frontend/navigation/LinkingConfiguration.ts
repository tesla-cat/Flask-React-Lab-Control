import * as Linking from 'expo-linking';

export default {
  prefixes: [Linking.makeUrl('https://tesla-cat.github.io/LabTools')],
  config: {
    screens: {
      Root: {
        screens: {
          TabOne: {
            screens: {
              TabOneScreen: 'one',
            },
          },
          TabTwo: {
            screens: {
              TabTwoScreen: 'two',
            },
          },
        },
      },
      NotFound: '*',
    },
  },
};

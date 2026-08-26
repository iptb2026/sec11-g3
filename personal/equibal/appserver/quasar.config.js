import { configure } from 'quasar/wrappers';

export default configure((/* ctx */) => {
  return {
    devServer: {
      port: 9003,
      open: false
    }
  };
});

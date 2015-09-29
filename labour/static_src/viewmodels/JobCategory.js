import _ from 'lodash';
import ko from 'knockout';
import page from 'page';

import {getJobCategory, saveJobCategory} from '../services/RosterService';


export default class JobCategory {
  constructor(app) {
    this.app = app;
    this.jobCategory = ko.observable(null);

    this.setupRoutes();
  }

  setupRoutes() {
    this.actions = {
      selectJobCategory: (ctx, next) => { getJobCategory(ctx.params.jobCategorySlug).then(this.jobCategory).then(next); },
      activate: (ctx) => { this.app.activeView('JobCategory'); },
    }

    page('/jobcategory/:jobCategorySlug',
      this.actions.selectJobCategory,
      this.actions.activate
    );
  }
}

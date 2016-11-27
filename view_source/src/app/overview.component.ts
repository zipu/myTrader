import { Component} from '@angular/core';
//import { Router } from '@angular/router-deprecated'

@Component({
  selector: 'my-overview',
  template: require('./overview.component.html'),
})

export class OverviewComponent{
  /**
  constructor(
    
  private kiwoomService: KiwoomService,
    private router: Router
  ) {}
  
  products: Product[];
  selectedProduct: Product;
  
  onselect(product: Product) {
    this.selectedProduct = product;
  }
  
  getProducts() {
    this.kiwoomService.getProducts().then(products => 
      this.products = products
    );
  }
  
  ngOnInit() {
    this.getProducts();
  }
  
  gotoDetail() {
    this.router.navigate(['ProductDetail', { id: this.selectedProduct.code }]);
  }
  */
}


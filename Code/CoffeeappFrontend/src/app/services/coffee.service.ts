import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, map, tap } from 'rxjs';

interface ManufacturersWithProducts {
  [manufacturer: string]: string[];
}

@Injectable({
  providedIn: 'root',
})
export class CoffeeService {
  private productsSubject =
    new BehaviorSubject<ManufacturersWithProducts | null>(null);
  products$ = this.productsSubject.asObservable();

  manufacturers$ = this.products$.pipe(
    map((products) => (products ? Object.keys(products) : []))
  );

  constructor(private http: HttpClient) {}

  getProductsForAllManufacturer() {
    return this.http
      .get<ManufacturersWithProducts>(
        `http://127.0.0.1:8000/getProductsForAllManufacturer/`
      )
      .pipe(
        tap((productsResponse) => {
          this.productsSubject.next(productsResponse);
        })
      );
  }

  getPredictedAnswers({
    manufacturer,
    product,
    question,
  }: {
    manufacturer: string;
    product: string;
    question: string;
  }) {
    const body = {
      manufacturer,
      product,
      question,
      language: 'en',
    };

    return this.http
      .post<any>('http://127.0.0.1:8000/getPredictedAnswers/', body)
      .pipe();
  }

  selectProductsForManufacturer(manufacturer: string) {
    return this.products$.pipe(
      map((products) => (products ? products[manufacturer] : []))
    );
  }
}

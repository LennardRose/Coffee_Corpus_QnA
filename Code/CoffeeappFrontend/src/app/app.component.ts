import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { filter, Observable, switchMap, tap } from 'rxjs';
import { CoffeeService } from './services/coffee.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {
  title = 'Coffeeapp_v2';

  coffeeForm!: FormGroup;

  manufacturers$!: Observable<string[]>;
  products$!: Observable<string[]>;

  answers: string[] = [];

  get manufacturerControl() {
    return this.coffeeForm.get('manufacturer');
  }

  constructor(private coffeeService: CoffeeService) {}

  ngOnInit() {
    this.coffeeForm = new FormGroup({
      manufacturer: new FormControl('', Validators.required),
      product: new FormControl('', Validators.required),
      question: new FormControl('', Validators.required),
    });

    this.manufacturers$ = this.coffeeService.manufacturers$;

    this.products$ = this.manufacturerControl!.valueChanges.pipe(
      switchMap((manufacturer) =>
        this.coffeeService.selectProductsForManufacturer(manufacturer)
      )
    );

    this.coffeeService.getProductsForAllManufacturer().subscribe();
  }

  sendQuestion() {
    if (this.coffeeForm.invalid) {
      return;
    }

    this.coffeeService
      .getPredictedAnswers(this.coffeeForm.value)
      .subscribe((answers) => {
        this.answers = answers;
      });
  }
}

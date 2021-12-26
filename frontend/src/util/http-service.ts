import axios, { AxiosRequestConfig, AxiosResponse } from "axios";
import Cookies from "js-cookie";
import _ from "lodash";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function camelizeKeys(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map(v => camelizeKeys(v));
  } else if (obj != null && obj.constructor === Object) {
    return Object.keys(obj).reduce(
      (result, key) => ({
        ...result,
        [_.camelCase(key)]: camelizeKeys(obj[key]),
      }),
      {},
    );
  }
  return obj;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function decamelizeKeys(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map(v => decamelizeKeys(v));
  } else if (obj != null && obj.constructor === Object) {
    return Object.keys(obj).reduce(
      (result, key) => ({
        ...result,
        [_.snakeCase(key)]: decamelizeKeys(obj[key]),
      }),
      {},
    );
  }
  return obj;
}


// eslint-disable-next-line @typescript-eslint/no-explicit-any
function fixResponseDataIfJsonParsingFailed(responseData: any) {
  if (!responseData) {
    // Response data is null
    return responseData;
  } else if (typeof responseData === 'string') {
    try {
      // Try to parse the response after replacing NaNs with nulls
      return JSON.parse(responseData.replace(/\bNaN\b/g, 'null'));
    } catch (e) {
      // The response was not JSON
      if (e instanceof SyntaxError) {
        throw new Error('The server returned an invalid response');
      } else {
        throw e;
      }
    }
  } else {
    return responseData;
  }
}

export default class HttpService {
  private static _axios = axios.create({
    transformRequest: [decamelizeKeys, JSON.stringify], // TODO: Perform decamelizing on backend
    transformResponse: [fixResponseDataIfJsonParsingFailed, camelizeKeys], // TODO: Perform camelizing on backend and send nulls instead of NaNs
    baseURL: '/',
  });

  static async get<TResponse>(url: string, successFn: (response: TResponse) => void, failureFn?: (response: ValidationErrorData) => void): Promise<void> {
    await this.performRequestFn(this._axios.get, url, successFn, failureFn);
  }

  static async post<TResponse, TRequest>(url: string, data: TRequest, successFn: (response: TResponse) => void, failureFn?: (response: ValidationErrorData) => void): Promise<void> {
    await this.performDataRequestFn(this._axios.post, url, data, successFn, failureFn);
  }

  static async put<TResponse, TRequest>(url: string, data: TRequest, successFn: (response: TResponse) => void, failureFn?: (response: ValidationErrorData) => void): Promise<void> {
    await this.performDataRequestFn(this._axios.put, url, data, successFn, failureFn);
  }

  static async delete<TResponse, TRequest>(url: string, data: TRequest, successFn: (response: TResponse) => void, failureFn?: (response: ValidationErrorData) => void): Promise<void> {
    await this.performDataRequestFn(this._axios.delete, url, data, successFn, failureFn);
  }


  private static async performRequestFn<TResponse>(axiosRequestFn: AxiosRequestFn<TResponse | ValidationErrorData>, url: string, successFn: (response: TResponse) => void, failureFn?: (response: ValidationErrorData) => void): Promise<void> {
    const response = await axiosRequestFn(url);
    this.processResponse(response, successFn, failureFn);
  }

  private static async performDataRequestFn<TResponse, TRequest>(axiosDataRequestFn: AxiosDataRequestFn<TResponse | ValidationErrorData>, url: string, data: TRequest, successFn: (response: TResponse) => void, failureFn?: (response: ValidationErrorData) => void): Promise<void> {
    const config: AxiosRequestConfig = {
      headers: {
        'X-CSRFToken': this.getCsrfToken(),
      },
    };
    const response = await axiosDataRequestFn(url, data, config);

    this.processResponse(response, successFn, failureFn);
  }


  private static processResponse<TResponse>(response: AxiosResponse<TResponse | ValidationErrorData>, successFn: (response: TResponse) => void, failureFn?: (response: ValidationErrorData) => void): void {
    if (this.isResponseSuccess(response)) {
      successFn(response.data);
    } else if (this.isResponseValidationErrorData(response)) {
      if (failureFn) {
        failureFn(response.data);
      } else {
        throw new Error('The server responded with validation errors, but no failure handler was given.');
      }
    } else {
      throw new Error('The server responded with invalid data.');
    }
  }


  private static isResponseSuccess<TResponse>(response: AxiosResponse<TResponse | ValidationErrorData>): response is AxiosResponse<TResponse> {
    return response.status >= 200 && response.status < 300;
  }

  private static isResponseValidationErrorData<TResponse>(response: AxiosResponse<TResponse | ValidationErrorData>): response is AxiosResponse<ValidationErrorData> {
    return response.status >= 400 && response.status < 600 && 'errors' in response.data;
  }


  private static getCsrfToken(): string {
    const csrfToken = Cookies.get('csrftoken');
    if (!csrfToken) throw new Error("No CSRF token.");
    return csrfToken;
  }
}

type AxiosRequestFn<T> = (url: string, config?: AxiosRequestConfig) => Promise<AxiosResponse<T>>;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AxiosDataRequestFn<T> = (url: string, data?: any, config?: AxiosRequestConfig) => Promise<AxiosResponse<T>>;

type ValidationErrorData = {
  errors: { global?: string[] } & { [key: string]: string[] }
};

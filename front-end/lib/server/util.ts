import { z, ZodType } from "zod";

export function logWrongServerResponseBody(
	received: any,
	expected: ZodType<any>
): void {
	console.error(
		`The server sent an unexpected result.\n`,
		`Expected a result that matches:\n`,
		`${JSON.stringify(z.toJSONSchema(expected))}\n`,
		`but received:\n`,
		`${JSON.stringify(received)}`
	)
}
